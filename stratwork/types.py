from enum import Enum
from dataclasses import dataclass

class PositionDirection(Enum):
    NONE = 0
    LONG = 1
    SHORT = -1

@dataclass
class Order:
    """Container to store an open order"""
    order_id: str
    client_order_id: str
    quantity: float
    price: float
