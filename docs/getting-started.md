# Getting Started

## Prerequisites

Before getting started with StratWork, ensure you have:

- Python 3.11 or higher
- Poetry (recommended) or pip
- API credentials for a supported cryptocurrency exchange

## Installation

### Method 1: Using Poetry (Recommended)

Poetry provides better dependency management and virtual environment handling:

```bash
# Clone the repository
git clone https://github.com/yourusername/stratwork.git
cd stratwork

# Install dependencies
poetry install

# Activate the virtual environment
poetry shell
```

### Method 2: Using pip

```bash
# Clone the repository
git clone https://github.com/yourusername/stratwork.git
cd stratwork

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## Exchange Setup

StratWork works with any exchange supported by CCXT. Here's how to set up common exchanges:

### Binance

```python
import ccxt

exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret',
    'sandbox': True,  # Use testnet for development
    'enableRateLimit': True,
})
```

### Coinbase Pro

```python
import ccxt

exchange = ccxt.coinbasepro({
    'apiKey': 'your_api_key',
    'secret': 'your_secret',
    'password': 'your_passphrase',
    'sandbox': True,
    'enableRateLimit': True,
})
```

## Your First Strategy

Let's create a simple strategy that opens a long position when certain conditions are met:

```python
import ccxt
from stratwork import PositionManager, StopPriceCalculator, TechnicalAnalysisCalculator

# Initialize exchange
exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret',
    'sandbox': True,
    'enableRateLimit': True,
})

# Create stop price calculator (2% stop loss)
stop_calculator = StopPriceCalculator(stop_loss_pct=2.0)

# Initialize position manager
position_manager = PositionManager(
    long_symbol='BTC',
    short_symbol='USDT',
    max_usd_pos=100,  # Maximum $100 position
    stop_price_calculator=stop_calculator,
    gain_target_pct=5.0,  # 5% profit target
    exchange=exchange,
    trading=False  # Set to True when ready to trade
)

# Simple strategy logic
def simple_strategy():
    # Check if we already have a position
    if position_manager.has_active_position():
        print("Position already active")
        return
    
    # Get current price data
    ticker = exchange.fetch_ticker('BTC/USDT')
    current_price = ticker['last']
    
    # Simple condition: open position if price is above a threshold
    if current_price > 50000:  # Example threshold
        print("Opening long position")
        position_manager.open_long_position()
    else:
        print(f"Waiting for better entry: {current_price}")

# Run the strategy
if __name__ == "__main__":
    simple_strategy()
```

## Testing Your Strategy

Always test your strategies thoroughly before using real money:

1. **Use Sandbox/Testnet**: All major exchanges provide test environments
2. **Paper Trading**: Set `trading=False` to simulate trades without execution
3. **Small Amounts**: Start with very small position sizes
4. **Monitor Closely**: Watch your first few trades carefully

## Configuration Best Practices

### Risk Management
```python
# Conservative settings
position_manager = PositionManager(
    max_usd_pos=50,        # Small position size
    gain_target_pct=2.0,   # Conservative profit target
    stop_loss_pct=1.0,     # Tight stop loss
    trading=False          # Paper trading first
)
```

### Production Settings
```python
# When ready for production
position_manager = PositionManager(
    max_usd_pos=500,       # Larger position size
    gain_target_pct=3.0,   # Balanced profit target
    stop_loss_pct=2.0,     # Reasonable stop loss
    trading=True           # Live trading
)
```

## Common Patterns

### Technical Analysis Integration

```python
from stratwork import TechnicalAnalysisCalculator, RingBuffer

# Create price buffer
price_buffer = RingBuffer(50)  # Store last 50 prices

# Calculate moving averages
def calculate_signals():
    prices = price_buffer.get_all()
    if len(prices) < 20:
        return None
    
    sma_20 = TechnicalAnalysisCalculator.sma(prices[-20:])
    sma_50 = TechnicalAnalysisCalculator.sma(prices[-50:]) if len(prices) >= 50 else None
    
    return {
        'sma_20': sma_20,
        'sma_50': sma_50,
        'current_price': prices[-1]
    }
```

### Error Handling

```python
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def robust_strategy():
    try:
        # Your strategy logic here
        position_manager.open_long_position()
    except Exception as e:
        logger.error(f"Strategy error: {e}")
        # Handle the error appropriately
```

## Next Steps

- Read the [API Reference](api-reference.md) for detailed documentation
- Check out [Examples](examples.md) for more complex strategies
- Learn about [Configuration](configuration.md) options
- Review [Best Practices](best-practices.md) for production use

## Troubleshooting

### Common Issues

**API Key Errors**
- Ensure API keys are correct and have trading permissions
- Check if IP whitelist is configured correctly

**Order Failures**
- Verify sufficient balance
- Check minimum order sizes for the exchange
- Ensure the trading pair is available

**Connection Issues**
- Enable rate limiting: `enableRateLimit: True`
- Check internet connection and exchange status
- Use appropriate timeout settings

For more help, visit our [GitHub Issues](https://github.com/yourusername/stratwork/issues) page. 