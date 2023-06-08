from stratwork.RingBuffer import RingBuffer
from abc import ABC, abstractmethod
import logging

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
    