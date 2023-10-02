from dataclasses import dataclass

@dataclass
class Point:
    """Container for a point"""
    x: float
    y: float

class TechnicalAnalysisCalculator:
    def __init__(self):
        pass
    
    @staticmethod
    def sma(items):
        if len(items) == 0:
            return None
        return sum(items)/len(items)

    @staticmethod
    def dydx(current: Point, previous: Point):
        dy = current.y - previous.y
        dx = current.x - previous.x
        if dx == 0.0:
            raise ZeroDivisionError
        return dy/dx
    
    @staticmethod
    def ema(price, previous_ema, period):
        if previous_ema is None:
            return price
        return price * TechnicalAnalysisCalculator.k(period) + previous_ema * (1-TechnicalAnalysisCalculator.k(period))

    @staticmethod
    def k(period):
        return 2/(period+1)
