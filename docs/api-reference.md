# API Reference

## Core Classes

### PositionManager

The main class for managing trading positions and executing trades.

#### Constructor

```python
PositionManager(long_symbol, short_symbol, max_usd_pos, stop_price_calculator, 
                gain_target_pct, exchange, trading, disable_stop_loss=False)
```

**Parameters:**
- `long_symbol` (str): The symbol to buy (e.g., 'BTC')
- `short_symbol` (str): The base currency symbol (e.g., 'USDT')
- `max_usd_pos` (float): Maximum position size in USD
- `stop_price_calculator` (StopPriceCalculator): Calculator for stop-loss prices
- `gain_target_pct` (float): Target profit percentage
- `exchange` (ccxt.Exchange): CCXT exchange instance
- `trading` (bool): Enable actual trading (False for paper trading)
- `disable_stop_loss` (bool, optional): Disable stop-loss orders

#### Methods

##### `open_long_position()`
Opens a long position based on current market conditions.

```python
position_manager.open_long_position()
```

**Returns:** None

**Behavior:**
1. Calculates available capital
2. Places market buy order
3. Sets profit target and stop-loss
4. Validates trade execution

##### `exit_position()`
Closes the current position with a market sell order.

```python
position_manager.exit_position()
```

**Returns:** None

##### `has_active_position()`
Checks if there's currently an active position.

```python
active = position_manager.has_active_position()
```

**Returns:** `bool` - True if position is active

##### `get_current_stop_price()`
Returns the current stop-loss price.

```python
stop_price = position_manager.get_current_stop_price()
```

**Returns:** `float` - Current stop price

##### `get_last_trade_price()`
Returns the price of the last executed trade.

```python
last_price = position_manager.get_last_trade_price()
```

**Returns:** `float` - Last trade price

##### `update_stop_order_price(price)`
Updates the stop-loss order to a new price.

```python
position_manager.update_stop_order_price(45000.0)
```

**Parameters:**
- `price` (float): New stop price

##### `fetch_free_capital()`
Retrieves available balance for trading.

```python
capital = position_manager.fetch_free_capital()
```

**Returns:** `float` - Available balance in short symbol

##### `fetch_allocated_position()`
Gets the current position size.

```python
position = position_manager.fetch_allocated_position()
```

**Returns:** `float` - Current position size in long symbol

---

### StopPriceCalculator

Calculates appropriate stop-loss prices based on various strategies.

#### Constructor

```python
StopPriceCalculator(stop_loss_pct)
```

**Parameters:**
- `stop_loss_pct` (float): Stop-loss percentage (e.g., 2.0 for 2%)

#### Methods

##### `calculate_stop_price(entry_price)`
Calculates the stop-loss price for a given entry price.

```python
stop_price = calculator.calculate_stop_price(50000.0)
```

**Parameters:**
- `entry_price` (float): Entry price of the position

**Returns:** `float` - Calculated stop price

---

### TechnicalAnalysisCalculator

Provides technical analysis calculations and indicators.

#### Static Methods

##### `sma(items)`
Calculates Simple Moving Average.

```python
sma_value = TechnicalAnalysisCalculator.sma([10, 12, 14, 16, 18])
```

**Parameters:**
- `items` (list): List of numeric values

**Returns:** `float` - Simple moving average, or `None` if list is empty

##### `ema(price, previous_ema, period)`
Calculates Exponential Moving Average.

```python
ema_value = TechnicalAnalysisCalculator.ema(50.0, 48.5, 20)
```

**Parameters:**
- `price` (float): Current price
- `previous_ema` (float): Previous EMA value (None for first calculation)
- `period` (int): EMA period

**Returns:** `float` - Exponential moving average

##### `dydx(current, previous)`
Calculates slope between two points.

```python
from stratwork.TechnicalAnalysisCalculator import Point

current_point = Point(x=10, y=100)
previous_point = Point(x=9, y=95)
slope = TechnicalAnalysisCalculator.dydx(current_point, previous_point)
```

**Parameters:**
- `current` (Point): Current point
- `previous` (Point): Previous point

**Returns:** `float` - Slope (dy/dx)

**Raises:** `ZeroDivisionError` if dx = 0

---

### RingBuffer

Efficient circular buffer for storing time-series data.

#### Constructor

```python
RingBuffer(size)
```

**Parameters:**
- `size` (int): Maximum buffer size

#### Methods

##### `add(item)`
Adds an item to the buffer.

```python
buffer = RingBuffer(10)
buffer.add(100.5)
```

**Parameters:**
- `item`: Item to add to buffer

##### `get_all()`
Returns all items in the buffer.

```python
items = buffer.get_all()
```

**Returns:** `list` - All items in buffer

##### `is_full()`
Checks if buffer is at capacity.

```python
full = buffer.is_full()
```

**Returns:** `bool` - True if buffer is full

##### `size()`
Returns current number of items.

```python
current_size = buffer.size()
```

**Returns:** `int` - Number of items in buffer

---

### TradeValidator

Validates trade execution and ensures orders are properly filled.

#### Static Methods

##### `is_valid_buy(trade, submission_time, symbol)`
Validates a buy trade execution.

```python
is_valid = TradeValidator.is_valid_buy(trade_data, datetime.now(), 'BTC/USDT')
```

**Parameters:**
- `trade` (dict): Trade data from exchange
- `submission_time` (datetime): When the order was submitted
- `symbol` (str): Trading pair symbol

**Returns:** `bool` - True if trade is valid

---

## Data Types

### PositionDirection

Enumeration for position directions.

```python
from stratwork.types import PositionDirection

# Values
PositionDirection.NONE   # 0
PositionDirection.LONG   # 1
PositionDirection.SHORT  # -1
```

### Order

Data class for storing order information.

```python
from stratwork.types import Order

order = Order(
    order_id="12345",
    client_order_id="client_123",
    quantity=0.1,
    price=50000.0
)
```

**Attributes:**
- `order_id` (str): Exchange order ID
- `client_order_id` (str): Client-side order ID
- `quantity` (float): Order quantity
- `price` (float): Order price

### Point

Data class for representing x,y coordinates in technical analysis.

```python
from stratwork.TechnicalAnalysisCalculator import Point

point = Point(x=10.0, y=100.0)
```

**Attributes:**
- `x` (float): X coordinate
- `y` (float): Y coordinate

---

## Exception Handling

StratWork uses standard Python exceptions. Common scenarios:

### ZeroDivisionError
Thrown by `dydx()` when calculating slope with zero time difference.

### Exchange Exceptions
CCXT exchange exceptions are passed through. Common ones include:
- `ccxt.NetworkError`: Connection issues
- `ccxt.ExchangeError`: Exchange-specific errors
- `ccxt.InsufficientFunds`: Not enough balance
- `ccxt.InvalidOrder`: Order parameters invalid

### Example Error Handling

```python
import ccxt
import logging

try:
    position_manager.open_long_position()
except ccxt.InsufficientFunds:
    logging.error("Insufficient funds for trade")
except ccxt.NetworkError:
    logging.error("Network connection error")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
```

---

## Configuration Constants

### PositionManager Constants

- `ORDERBOOK_LEVELS = 20`: Number of orderbook levels to fetch
- `FETCH_LAST_TRADE_DELAY = 1`: Delay between trade validation checks

These constants are defined in the module but can be customized by modifying the source code if needed. 