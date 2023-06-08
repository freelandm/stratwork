from stratwork.RingBuffer import RingBuffer
from stratwork.exceptions import OrderbookMissingOrdersException
import logging
import pytz
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from time import sleep

# CONFIGURATION
DATE_FORMAT="%Y-%m-%dT%H:%M:%S.%fZ"
LAST_TRADE_OFFSET_TIME = 10


class StopPriceCalculator(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def calculate_stop_price(self):
        """Returns stop price according to specific calculation"""
        pass

class EMADxStopPriceCalculator(StopPriceCalculator):
    def __init__(self, stop_loss_pct):
        self._stop_loss_pct = stop_loss_pct
        logging.info(f'EMADxStopPriceCalculator initialize. {self._stop_loss_pct=}')

    def calculate_stop_price(self, price):
        return price - ((self._stop_loss_pct/100) * price)
    
class EMACStopPriceCalculator(StopPriceCalculator):
    def __init__(self, ema_100: RingBuffer, max_loss_percent):
        self._ema_100 = ema_100
        self._max_loss_percent = max_loss_percent
        logging.info(f'EMACStopPriceCalculator initialize. {self._ema_100=} {self._max_loss_percent}')

    def calculate_stop_price(self, price):
        return max(self._ema_100.get_most_recent(), price*(1-self._max_loss_percent/100))
    
class TradeValidator:
    @staticmethod
    def is_valid_buy(last_trade, trade_submission_dt, symbol):
        return TradeValidator.is_valid(last_trade=last_trade, trade_submission_dt=trade_submission_dt, symbol=symbol, side="buy")
    @staticmethod
    def is_valid(last_trade, trade_submission_dt, symbol, side):
        if last_trade is None:
            return False
        def exists(key):
            if last_trade.get(key) is None:
                logging.error(f'LAST TRADE INVALID: NO {key.upper()}')
                return False
            return True
        # - did it happen within last N (5) seconds?
        if not exists('datetime'):
            return False
        last_trade_dt = pytz.utc.localize(datetime.strptime(last_trade.get('datetime'), DATE_FORMAT))
        if last_trade_dt - trade_submission_dt > timedelta(seconds=LAST_TRADE_OFFSET_TIME):
            logging.error(f'LAST TRADE INVALID: DATETIME (delta={last_trade_dt-trade_submission_dt})')
            return False
        # - is it expected symbol?
        if not exists('symbol'):
            return False
        if last_trade['symbol'].lower() != symbol.lower():
            logging.error(f'LAST TRADE INVALID: SYMBOL ({last_trade["symbol"]=})')
            return False
        # - is it expected side?
        if not exists('side'):
            return False
        if last_trade['side'].lower() != side.lower():
            logging.error(f'LAST TRADE INVALID: SIDE ({last_trade["side"]})')
            return False
        # - does it have a price?
        if not exists('price'):
            return False
        return True


class Calculator:
    @staticmethod
    def calculate_price_from_orderbook(orderbook, side):
        logging.info('Calculate price From OrderBook')
        orders = orderbook.get(side, None)
        if orders is None or len(orders) == 0:
            raise OrderbookMissingOrdersException
        return orders[0][0]

    @staticmethod
    def calculate_bid_from_orderbook(orderbook):
        return Calculator.calculate_price_from_orderbook(orderbook, 'bids')
        
    @staticmethod
    def calculate_ask_from_orderbook(orderbook):
        return Calculator.calculate_price_from_orderbook(orderbook, 'asks')
    
    @staticmethod
    def calculate_size_from_balance_and_price(balance, price):
        return balance / price
    