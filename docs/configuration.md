# Configuration

This guide covers all configuration options available in StratWork.

## PositionManager Configuration

### Basic Parameters

```python
PositionManager(
    long_symbol='BTC',           # Symbol to buy
    short_symbol='USDT',         # Base currency
    max_usd_pos=1000,           # Maximum position size
    stop_price_calculator=calc,  # Stop loss calculator
    gain_target_pct=3.0,        # Profit target percentage
    exchange=exchange,          # CCXT exchange instance
    trading=True,               # Enable live trading
    disable_stop_loss=False     # Disable stop loss orders
)
```

#### Parameter Details

**`long_symbol`** (str)
- The cryptocurrency symbol to purchase
- Examples: 'BTC', 'ETH', 'ADA', 'DOT'
- Must be supported by your chosen exchange

**`short_symbol`** (str)  
- The base currency for trading
- Commonly: 'USDT', 'USDC', 'USD', 'EUR'
- Used for calculating position sizes and profits

**`max_usd_pos`** (float)
- Maximum position size in USD equivalent
- Acts as a risk management control
- Example: `1000` limits positions to $1000 maximum

**`gain_target_pct`** (float)
- Target profit percentage for positions
- Example: `3.0` means 3% profit target
- Used to automatically close profitable positions

**`trading`** (bool)
- Controls whether actual trades are executed
- `False`: Paper trading mode (simulation only)
- `True`: Live trading with real money
- **Always start with `False` for testing**

**`disable_stop_loss`** (bool, optional)
- Whether to skip stop-loss order placement
- Default: `False` (stop losses enabled)
- Set to `True` for manual risk management

### Risk Management Settings

```python
# Conservative settings
PositionManager(
    max_usd_pos=100,        # Small position size
    gain_target_pct=1.5,    # Conservative profit target
    trading=False,          # Paper trading
    disable_stop_loss=False # Keep stop losses enabled
)

# Aggressive settings  
PositionManager(
    max_usd_pos=5000,       # Larger position size
    gain_target_pct=5.0,    # Higher profit target
    trading=True,           # Live trading
    disable_stop_loss=False # Still use stop losses
)
```

## StopPriceCalculator Configuration

### Basic Setup

```python
from stratwork import StopPriceCalculator

# Percentage-based stop loss
stop_calc = StopPriceCalculator(stop_loss_pct=2.0)  # 2% stop loss
```

### Advanced Stop Loss Strategies

```python
# Conservative (tight stop)
conservative_calc = StopPriceCalculator(stop_loss_pct=1.0)

# Moderate 
moderate_calc = StopPriceCalculator(stop_loss_pct=2.5)

# Loose (for volatile markets)
loose_calc = StopPriceCalculator(stop_loss_pct=5.0)
```

### Custom Stop Loss Implementation

You can create custom stop loss calculators:

```python
class ATRStopCalculator:
    """Stop loss based on Average True Range"""
    
    def __init__(self, atr_multiplier=2.0):
        self.atr_multiplier = atr_multiplier
        
    def calculate_stop_price(self, entry_price):
        # Implement ATR-based stop loss
        # This is a simplified example
        atr = self.calculate_atr()  # Your ATR calculation
        stop_distance = atr * self.atr_multiplier
        return entry_price - stop_distance
    
    def calculate_atr(self):
        # Implement ATR calculation
        return 100  # Placeholder
```

## Exchange Configuration

### Binance Setup

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret',
    'sandbox': True,                # Use testnet
    'enableRateLimit': True,        # Respect rate limits
    'options': {
        'defaultType': 'spot',      # Spot trading
        'adjustForTimeDifference': True
    }
})
```

### Common Exchange Settings

```python
# General configuration for most exchanges
exchange_config = {
    'enableRateLimit': True,        # Essential for stability
    'sandbox': True,                # Use for testing
    'timeout': 30000,              # 30 second timeout
    'rateLimit': 1200,             # Milliseconds between requests
}

# Apply to any exchange
exchange = ccxt.binance(exchange_config)
```

## Environment-Based Configuration

### Using Environment Variables

```python
import os
from stratwork import PositionManager, StopPriceCalculator

# Load from environment
config = {
    'api_key': os.getenv('EXCHANGE_API_KEY'),
    'secret': os.getenv('EXCHANGE_SECRET'),
    'max_position': float(os.getenv('MAX_POSITION_USD', '100')),
    'profit_target': float(os.getenv('PROFIT_TARGET_PCT', '2.0')),
    'stop_loss': float(os.getenv('STOP_LOSS_PCT', '1.5')),
    'trading_enabled': os.getenv('TRADING_ENABLED', 'false').lower() == 'true'
}

# Setup components
exchange = ccxt.binance({
    'apiKey': config['api_key'],
    'secret': config['secret'],
    'sandbox': not config['trading_enabled'],
    'enableRateLimit': True,
})

stop_calc = StopPriceCalculator(stop_loss_pct=config['stop_loss'])

position_manager = PositionManager(
    long_symbol='BTC',
    short_symbol='USDT',
    max_usd_pos=config['max_position'],
    stop_price_calculator=stop_calc,
    gain_target_pct=config['profit_target'],
    exchange=exchange,
    trading=config['trading_enabled']
)
```

### Configuration File

```python
import json
from pathlib import Path

def load_config(config_path='config.json'):
    """Load configuration from JSON file"""
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        return json.load(f)

# Example config.json
config_example = {
    "exchange": {
        "name": "binance",
        "api_key": "your_api_key",
        "secret": "your_secret",
        "sandbox": true
    },
    "trading": {
        "max_position_usd": 500,
        "profit_target_pct": 2.5,
        "stop_loss_pct": 1.8,
        "trading_enabled": false
    },
    "symbols": {
        "long": "BTC",
        "short": "USDT"
    }
}
```

## Technical Analysis Configuration

### RingBuffer Settings

```python
from stratwork import RingBuffer

# For different analysis periods
short_term_buffer = RingBuffer(20)   # 20-period analysis
medium_term_buffer = RingBuffer(50)  # 50-period analysis  
long_term_buffer = RingBuffer(200)   # 200-period analysis
```

### Technical Indicators Configuration

```python
# EMA periods
ema_fast_period = 12
ema_slow_period = 26

# SMA periods
sma_short_period = 10
sma_long_period = 30

# Bollinger Bands
bb_period = 20
bb_std_dev = 2.0
```

## Logging Configuration

### Basic Logging Setup

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('stratwork.log'),
        logging.StreamHandler()
    ]
)

# Create logger for your strategy
logger = logging.getLogger('strategy')
```

### Advanced Logging

```python
import logging
from logging.handlers import RotatingFileHandler

# Setup rotating log files
def setup_logging():
    logger = logging.getLogger('stratwork')
    logger.setLevel(logging.INFO)
    
    # Rotating file handler (10MB max, keep 5 files)
    file_handler = RotatingFileHandler(
        'stratwork.log', 
        maxBytes=10*1024*1024, 
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s')
    )
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

## Performance Optimization

### Rate Limiting

```python
# Optimize for exchange rate limits
exchange = ccxt.binance({
    'enableRateLimit': True,
    'rateLimit': 1200,  # Milliseconds between requests
    'options': {
        'rateLimit': 1200,
        'enableRateLimit': True,
    }
})
```

### Memory Management

```python
# Limit buffer sizes to manage memory
class MemoryEfficientStrategy:
    def __init__(self):
        # Use smaller buffers for memory efficiency
        self.price_buffer = RingBuffer(100)  # Instead of 1000+
        
    def cleanup_old_data(self):
        """Periodically clean up old data"""
        # Implement data cleanup logic
        pass
```

## Testing Configuration

### Sandbox/Testnet Settings

```python
# Test configuration
test_config = {
    'exchange': {
        'sandbox': True,
        'enableRateLimit': True,
    },
    'position_manager': {
        'max_usd_pos': 10,      # Very small for testing
        'trading': False,        # Paper trading
        'gain_target_pct': 1.0,  # Small target for quick tests
    }
}
```

### Backtesting Configuration

```python
# Configuration for historical testing
backtest_config = {
    'start_date': '2023-01-01',
    'end_date': '2023-12-31',
    'initial_balance': 1000,
    'commission_rate': 0.001,  # 0.1% commission
    'slippage': 0.0005,        # 0.05% slippage
}
```

## Configuration Validation

```python
def validate_config(config):
    """Validate configuration parameters"""
    required_fields = ['api_key', 'secret', 'max_position']
    
    for field in required_fields:
        if field not in config or not config[field]:
            raise ValueError(f"Missing required config field: {field}")
    
    if config.get('max_position', 0) <= 0:
        raise ValueError("max_position must be positive")
    
    if config.get('profit_target', 0) <= 0:
        raise ValueError("profit_target must be positive")
        
    return True

# Usage
try:
    validate_config(config)
    print("Configuration is valid")
except ValueError as e:
    print(f"Configuration error: {e}")
```

## Best Practices

1. **Start Small**: Begin with small position sizes and conservative settings
2. **Use Sandbox**: Always test in sandbox/testnet environments first
3. **Environment Variables**: Store sensitive data in environment variables
4. **Logging**: Enable comprehensive logging for debugging
5. **Validation**: Validate all configuration parameters
6. **Rate Limits**: Respect exchange rate limits
7. **Error Handling**: Implement robust error handling
8. **Monitoring**: Set up monitoring and alerting for production use 