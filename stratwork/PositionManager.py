from datetime import datetime
from stratwork.Calculator import Calculator
from stratwork.StopPriceCalculator import StopPriceCalculator
from stratwork.TradeValidator import TradeValidator
from stratwork.types import Order, PositionDirection
from ccxt import Exchange
from time import sleep
import pytz
import logging

ORDERBOOK_LEVELS = 20
FETCH_LAST_TRADE_DELAY = 1

class PositionManager:
    def __init__(self, long_symbol, short_symbol, max_usd_pos, stop_price_calculator, gain_target_pct, exchange, trading, disable_stop_loss = False):
        self._symbol = "/".join([long_symbol, short_symbol])
        self._long_symbol = long_symbol
        self._short_symbol = short_symbol
        self._max_usd_pos = max_usd_pos
        self._direction = PositionDirection.NONE
        self._balance_difference_threshold = 0.1
        self._exchange: Exchange = exchange
        self._stop_price_calculator: StopPriceCalculator = stop_price_calculator
        self._max_number_of_last_trade_checks = 10
        self._trading = trading
        self._gain_target_pct = gain_target_pct # some random number between [min_target, max_target] threshold
        self._profit_target_price = None
        self._stop_price = None
        self._last_trade_price = None
        self._disable_stop_loss = disable_stop_loss
        logging.info(f'PositionManager initialized. {long_symbol=} {short_symbol=} {max_usd_pos=} {gain_target_pct=}')

    def get_current_stop_price(self):
        return self._stop_price

    def get_last_trade_price(self):
        return self._last_trade_price

    def open_long_position(self):
        logging.info(f'OPEN LONG POS')
        free_capital = self.fetch_free_capital()
        max_spend = min(self._max_usd_pos, free_capital)
        ask = Calculator.calculate_ask_from_orderbook(self._exchange.fetch_order_book(self._symbol, ORDERBOOK_LEVELS))
        amount = max_spend/ask
        logging.info(f'SUBMIT MARKET BUY ORDER | {max_spend=} {free_capital=} {self._max_usd_pos=} {ask=} {amount=}')
        if self._trading is not True:
            logging.info(f'TRADING FLAG DISABLED')
            return
        enter_pos_order_response = self._exchange.create_market_buy_order(self._symbol, amount=amount)
        trade_submission_dt = datetime.now(tz=pytz.utc)
        logging.info(f'BUY ORDER RESPONSE {enter_pos_order_response}')
        allocated_position = self.fetch_allocated_position()
        logging.info(f'{self._short_symbol} | {allocated_position=}')
        number_of_checks = 0
        last_trade = self.fetch_last_trade()
        while not TradeValidator.is_valid_buy(last_trade, trade_submission_dt, self._symbol) and number_of_checks <= self._max_number_of_last_trade_checks:
            last_trade = self.fetch_last_trade()
            # esperate
            sleep(FETCH_LAST_TRADE_DELAY)

        if not TradeValidator.is_valid_buy(last_trade, trade_submission_dt, self._symbol):
            # something is wrong, close all positions
            logging.error(f'LAST TRADE INVALID | CLOSING POSITIONS')
            self.close_stop_order()
            self.exit_position()
            return

        self._last_trade_price = last_trade['price']
        # calculate profit_target_price
        logging.info(f'LAST TRADE: price={last_trade["price"]} amount={last_trade["amount"]}')

        self._profit_target_price = self._last_trade_price + (self._gain_target_pct/100)*self._last_trade_price
        stop_price = self._stop_price_calculator.calculate_stop_price(self._last_trade_price)
        self._allocated_position = allocated_position
        logging.info(f'SET PROFIT TARGET: {self._profit_target_price} ({self._gain_target_pct}%)')
        self.submit_stop_order(stop_price)

    def submit_stop_order(self, stop_price):
        if self._disable_stop_loss:
            logging.info('SKIPPING STOP LOSS | DISABLED')
            return
        logging.info(f'SUBMIT STOP LOSS | {self._symbol}:{self._allocated_position}@{stop_price}')
        self._stop_price = stop_price
        stop_order_response = self._exchange.create_stop_market_order(self._symbol, 'sell', self._allocated_position, stop_price)
        logging.info(f'STOP LOSS ORDER RESPONSE {stop_order_response}')

    def update_stop_order_price(self, price):
        # needs to cancel previous order
        logging.info(f'CANCEL/REPLACE STOP ORDER: {price=}')
        if price == self._stop_price:
            logging.info(f'NO PRICE CHANGE | NOT UPDATING')
            return
        self.close_stop_order()
        self.submit_stop_order(price)

    def exit_position(self):
        logging.info(f'EXIT POSITION')
        amount = self.fetch_allocated_position()
        logging.info(f'SUBMIT MARKET SELL ORDER | {amount=}')
        exit_pos_order_response = self._exchange.create_market_sell_order(self._symbol, amount)
        logging.info(f'EXIT POSITION RESPONSE {exit_pos_order_response}')
        return
    
    def close_stop_order(self):
        logging.info(f'CLOSE STOP ORDER')
        stop_orders = self.fetch_stop_orders()
        if len(stop_orders) <= 0:
            logging.warning(f'STOP ORDER DOES NOT EXIST')
            return
        for stop_order in stop_orders:
            logging.info(f'STOP ORDER: {stop_order}')
            response = self._exchange.cancel_order(stop_order.order_id, self._symbol, {'clientOrderId': stop_order.client_order_id, 'stop': True})
            logging.info(f"CLOSE STATUS: {'SUCCESS' if response is True else 'FAIL'}")

    def fetch_last_trade(self):
        logging.info(f'FETCH LAST TRADE')
        trades = self._exchange.fetch_closed_orders(self._symbol)
        if len(trades) <= 0:
            return None
        return trades[-1]

    def fetch_open_orders(self, params={}):
        logging.info(f'FETCH OPEN ORDERS')
        open_orders = self._exchange.fetch_open_orders(symbol=self._symbol, params=params)
        if len(open_orders) <= 0:
            return []
        return [o for o in open_orders if o['symbol'] == self._symbol]
    
    def fetch_stop_orders(self):
        logging.info(f'FETCH STOP ORDER')
        open_orders = self.fetch_open_orders({'stop': True})
        return [Order(o['id'], o['clientOrderId'], o['amount'], o['price']) for o in open_orders]

    def fetch_free_capital(self):
        logging.info(f'FETCH FREE CAPITAL')
        balances = self._exchange.fetch_balance()
        return balances[self._short_symbol]['free']

    def fetch_allocated_position(self):
        logging.info(f'FETCH ALLOCATED POSITION')
        balances = self._exchange.fetch_balance()
        return balances[self._long_symbol]['free']

    def has_active_position(self) -> bool:
        return len(self.fetch_stop_orders()) > 0
    
    @staticmethod
    def compare_balance(b1, b2, threshold=0):
        for b1_token_symbol,b1_token_balance in b1.items():
            b2_token_balance = b2.get(b1_token_symbol)
            if b2_token_balance is not None:
                if abs(abs(b1_token_balance) - abs(b2_token_balance)) > threshold:
                    return False
        return True