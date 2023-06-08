import logging
import pytz
from datetime import datetime, timedelta

# CONFIGURATION
DATE_FORMAT="%Y-%m-%dT%H:%M:%S.%fZ"
LAST_TRADE_OFFSET_TIME = 10


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

