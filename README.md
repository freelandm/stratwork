# StratWork

**CCXT Strategy Framework** - A Python trading framework built on top of [CCXT](https://github.com/ccxt/ccxt) for developing and executing cryptocurrency trading strategies.

[![Python](https://img.shields.io/badge/python-^3.11-blue.svg)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/poetry-dependency%20management-blue.svg)](https://python-poetry.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue.svg)](https://yourusername.github.io/stratwork)

## Overview

StratWork is a comprehensive trading framework designed to simplify the development of cryptocurrency trading strategies. Built as a wrapper around CCXT, it provides essential components for position management, technical analysis, risk management, and trade validation.

## Features

- **Position Management**: Comprehensive position tracking with automated entry/exit logic
- **Technical Analysis**: Built-in indicators including SMA, EMA, and slope calculations
- **Risk Management**: Configurable stop-loss and profit target mechanisms
- **Trade Validation**: Automated trade verification and error handling
- **Exchange Integration**: Seamless integration with 100+ cryptocurrency exchanges via CCXT
- **Flexible Architecture**: Modular design for easy strategy customization

## Installation

### Using Poetry (Recommended)

```bash
git clone https://github.com/yourusername/stratwork.git
cd stratwork
poetry install
```

### Using pip

```bash
git clone https://github.com/yourusername/stratwork.git
cd stratwork
pip install -e .
```

## Quick Start

```python
import ccxt
from stratwork import PositionManager, StopPriceCalculator

# Initialize exchange
exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret',
    'sandbox': True,  # Use testnet
})

# Create stop price calculator
stop_calculator = StopPriceCalculator(stop_loss_pct=2.0)

# Initialize position manager
position_manager = PositionManager(
    long_symbol='BTC',
    short_symbol='USDT',
    max_usd_pos=1000,
    stop_price_calculator=stop_calculator,
    gain_target_pct=3.0,
    exchange=exchange,
    trading=True
)

# Open a long position
position_manager.open_long_position()
```

## Core Components

### PositionManager
Handles position lifecycle management including entry, exit, and risk management.

### TechnicalAnalysisCalculator
Provides common technical indicators:
- Simple Moving Average (SMA)
- Exponential Moving Average (EMA)
- Slope calculations (dy/dx)

### StopPriceCalculator
Calculates appropriate stop-loss prices based on configurable parameters.

### TradeValidator
Validates trade execution and ensures orders are properly filled.

### RingBuffer
Efficient circular buffer implementation for storing price data and indicators.

## Configuration

The framework uses a flexible configuration system. Key parameters include:

- `max_usd_pos`: Maximum position size in USD
- `gain_target_pct`: Profit target percentage
- `stop_loss_pct`: Stop loss percentage
- `trading`: Enable/disable actual trading (useful for backtesting)

## Examples

Check out the `/examples` directory for comprehensive usage examples:

- Basic trading strategy
- Technical analysis integration
- Risk management examples
- Multi-exchange setup

## Testing

Run the test suite:

```bash
poetry run pytest
```

## Documentation

Full documentation is available at [https://yourusername.github.io/stratwork](https://yourusername.github.io/stratwork)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Roadmap

- [ ] Backtesting framework
- [ ] Strategy performance analytics
- [ ] More technical indicators
- [ ] Portfolio management
- [ ] Web-based dashboard
- [ ] Strategy optimization tools

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

**⚠️ Trading cryptocurrencies involves substantial risk of loss. This software is provided for educational purposes only. Always test strategies thoroughly in a sandbox environment before using real funds. The authors are not responsible for any financial losses.**

## Support

- 📖 [Documentation](https://yourusername.github.io/stratwork)
- 🐛 [Issue Tracker](https://github.com/yourusername/stratwork/issues)
- 💬 [Discussions](https://github.com/yourusername/stratwork/discussions)

---

Made with ❤️ by [Matt Freeland](https://github.com/yourusername)

