from stratwork.exceptions import OrderbookMissingOrdersException
import logging

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
    