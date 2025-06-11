# Best Practices

This guide outlines best practices for developing, testing, and deploying trading strategies using StratWork.

## Development Best Practices

### Code Organization

```python
# Good: Organized strategy structure
class TradingStrategy:
    def __init__(self, config):
        self.config = config
        self.setup_components()
        self.setup_logging()
    
    def setup_components(self):
        """Initialize all components"""
        pass
    
    def setup_logging(self):
        """Configure logging"""
        pass
    
    def analyze_market(self):
        """Market analysis logic"""
        pass
    
    def execute_trades(self):
        """Trade execution logic"""
        pass
    
    def manage_risk(self):
        """Risk management logic"""
        pass
```

### Error Handling

```python
import logging
from typing import Optional

class RobustStrategy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def safe_execute(self, operation_name: str, operation_func, *args, **kwargs):
        """Safely execute operations with comprehensive error handling"""
        try:
            result = operation_func(*args, **kwargs)
            self.logger.info(f"{operation_name} completed successfully")
            return result
        except ccxt.NetworkError as e:
            self.logger.error(f"Network error in {operation_name}: {e}")
            return None
        except ccxt.ExchangeError as e:
            self.logger.error(f"Exchange error in {operation_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in {operation_name}: {e}")
            return None
    
    def open_position_safely(self):
        """Example of safe position opening"""
        return self.safe_execute(
            "open_position",
            self.position_manager.open_long_position
        )
```

### Configuration Management

```python
from dataclasses import dataclass
from typing import Dict, Any
import os

@dataclass
class TradingConfig:
    """Structured configuration class"""
    api_key: str
    secret: str
    max_position_usd: float
    profit_target_pct: float
    stop_loss_pct: float
    trading_enabled: bool = False
    sandbox: bool = True
    
    @classmethod
    def from_env(cls) -> 'TradingConfig':
        """Load configuration from environment variables"""
        return cls(
            api_key=os.getenv('API_KEY', ''),
            secret=os.getenv('API_SECRET', ''),
            max_position_usd=float(os.getenv('MAX_POSITION_USD', '100')),
            profit_target_pct=float(os.getenv('PROFIT_TARGET_PCT', '2.0')),
            stop_loss_pct=float(os.getenv('STOP_LOSS_PCT', '1.5')),
            trading_enabled=os.getenv('TRADING_ENABLED', 'false').lower() == 'true',
            sandbox=os.getenv('SANDBOX', 'true').lower() == 'true'
        )
    
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.api_key or not self.secret:
            raise ValueError("API credentials are required")
        if self.max_position_usd <= 0:
            raise ValueError("max_position_usd must be positive")
        if self.profit_target_pct <= 0:
            raise ValueError("profit_target_pct must be positive")
        return True
```

## Risk Management

### Position Sizing

```python
class PositionSizer:
    """Calculate appropriate position sizes"""
    
    def __init__(self, max_risk_per_trade: float = 0.02):
        self.max_risk_per_trade = max_risk_per_trade  # 2% max risk
    
    def calculate_position_size(self, account_balance: float, 
                              entry_price: float, 
                              stop_price: float) -> float:
        """Calculate position size based on risk"""
        risk_per_share = abs(entry_price - stop_price)
        max_risk_amount = account_balance * self.max_risk_per_trade
        
        if risk_per_share == 0:
            return 0
            
        position_size = max_risk_amount / risk_per_share
        return min(position_size, account_balance * 0.1)  # Never risk more than 10%
```

### Stop Loss Management

```python
class DynamicStopLoss:
    """Dynamic stop loss adjustment"""
    
    def __init__(self, initial_stop_pct: float = 2.0):
        self.initial_stop_pct = initial_stop_pct
        self.trailing_active = False
        
    def calculate_stop_price(self, entry_price: float, 
                           current_price: float, 
                           profit_pct: float) -> float:
        """Calculate dynamic stop price"""
        initial_stop = entry_price * (1 - self.initial_stop_pct / 100)
        
        # Activate trailing stop after 1% profit
        if profit_pct > 1.0 and not self.trailing_active:
            self.trailing_active = True
        
        if self.trailing_active:
            # Trail stop at breakeven + 0.5%
            trailing_stop = entry_price * 1.005
            return max(initial_stop, trailing_stop)
        
        return initial_stop
```

## Testing Strategies

### Unit Testing

```python
import unittest
from unittest.mock import Mock, patch
from stratwork import TechnicalAnalysisCalculator

class TestTechnicalAnalysis(unittest.TestCase):
    
    def test_sma_calculation(self):
        """Test SMA calculation"""
        prices = [10, 12, 14, 16, 18]
        expected_sma = 14.0
        actual_sma = TechnicalAnalysisCalculator.sma(prices)
        self.assertEqual(actual_sma, expected_sma)
    
    def test_sma_empty_list(self):
        """Test SMA with empty list"""
        result = TechnicalAnalysisCalculator.sma([])
        self.assertIsNone(result)
    
    def test_ema_calculation(self):
        """Test EMA calculation"""
        price = 50.0
        previous_ema = 48.0
        period = 10
        
        expected_k = 2 / (period + 1)
        expected_ema = price * expected_k + previous_ema * (1 - expected_k)
        
        actual_ema = TechnicalAnalysisCalculator.ema(price, previous_ema, period)
        self.assertAlmostEqual(actual_ema, expected_ema, places=6)

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
class TestStrategyIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        self.mock_exchange = Mock()
        self.mock_exchange.fetch_ticker.return_value = {'last': 50000}
        self.mock_exchange.fetch_balance.return_value = {
            'USDT': {'free': 1000},
            'BTC': {'free': 0}
        }
        
    def test_position_opening(self):
        """Test position opening flow"""
        # Mock successful order
        self.mock_exchange.create_market_buy_order.return_value = {
            'id': '12345',
            'status': 'closed'
        }
        
        # Test strategy execution
        # Add your strategy testing logic here
        pass
```

### Backtesting Framework

```python
from datetime import datetime, timedelta
from typing import List, Dict

class SimpleBacktester:
    """Simple backtesting framework"""
    
    def __init__(self, initial_balance: float = 10000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = []
        self.trades = []
        
    def add_historical_data(self, data: List[Dict]):
        """Add historical price data"""
        self.historical_data = data
        
    def run_backtest(self, strategy_func):
        """Run backtest with given strategy"""
        for data_point in self.historical_data:
            # Simulate strategy execution
            signal = strategy_func(data_point)
            if signal:
                self.execute_trade(signal, data_point)
                
        return self.calculate_results()
    
    def execute_trade(self, signal: Dict, data: Dict):
        """Execute trade based on signal"""
        # Implement trade execution logic
        pass
    
    def calculate_results(self) -> Dict:
        """Calculate backtest results"""
        total_return = (self.balance - self.initial_balance) / self.initial_balance
        return {
            'total_return': total_return,
            'total_trades': len(self.trades),
            'final_balance': self.balance
        }
```

## Production Deployment

### Environment Setup

```python
# production_config.py
import os
from dataclasses import dataclass

@dataclass
class ProductionConfig:
    # Never hardcode credentials
    api_key: str = os.getenv('PROD_API_KEY')
    secret: str = os.getenv('PROD_API_SECRET')
    
    # Production settings
    trading_enabled: bool = True
    sandbox: bool = False
    
    # Risk management
    max_daily_loss: float = float(os.getenv('MAX_DAILY_LOSS', '500'))
    max_position_size: float = float(os.getenv('MAX_POSITION_SIZE', '1000'))
    
    # Monitoring
    alert_webhook: str = os.getenv('ALERT_WEBHOOK_URL', '')
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
```

### Monitoring and Alerting

```python
import requests
import logging
from datetime import datetime

class AlertManager:
    """Handle alerts and notifications"""
    
    def __init__(self, webhook_url: str = None):
        self.webhook_url = webhook_url
        self.logger = logging.getLogger(__name__)
        
    def send_alert(self, message: str, level: str = 'INFO'):
        """Send alert notification"""
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            'source': 'StratWork'
        }
        
        self.logger.log(getattr(logging, level), message)
        
        if self.webhook_url:
            try:
                requests.post(self.webhook_url, json=alert_data, timeout=10)
            except Exception as e:
                self.logger.error(f"Failed to send alert: {e}")
    
    def alert_position_opened(self, symbol: str, size: float, price: float):
        """Alert when position is opened"""
        message = f"Position opened: {size} {symbol} at {price}"
        self.send_alert(message, 'INFO')
    
    def alert_stop_loss_hit(self, symbol: str, loss: float):
        """Alert when stop loss is triggered"""
        message = f"Stop loss triggered for {symbol}, Loss: ${loss:.2f}"
        self.send_alert(message, 'WARNING')
    
    def alert_daily_loss_limit(self, loss: float):
        """Alert when daily loss limit is reached"""
        message = f"Daily loss limit reached: ${loss:.2f}"
        self.send_alert(message, 'CRITICAL')
```

### Health Checks

```python
from datetime import datetime, timedelta

class HealthChecker:
    """Monitor strategy health"""
    
    def __init__(self):
        self.last_heartbeat = datetime.now()
        self.error_count = 0
        self.max_errors = 10
        
    def heartbeat(self):
        """Update heartbeat timestamp"""
        self.last_heartbeat = datetime.now()
        
    def check_health(self) -> Dict[str, Any]:
        """Perform health check"""
        now = datetime.now()
        time_since_heartbeat = now - self.last_heartbeat
        
        health_status = {
            'status': 'healthy',
            'last_heartbeat': self.last_heartbeat.isoformat(),
            'error_count': self.error_count,
            'uptime': time_since_heartbeat.total_seconds()
        }
        
        # Check if strategy is responsive
        if time_since_heartbeat > timedelta(minutes=10):
            health_status['status'] = 'unresponsive'
            
        # Check error rate
        if self.error_count > self.max_errors:
            health_status['status'] = 'critical'
            
        return health_status
    
    def record_error(self):
        """Record an error occurrence"""
        self.error_count += 1
```

## Security Best Practices

### API Key Management

```python
# Good: Use environment variables
import os
api_key = os.getenv('API_KEY')

# Bad: Hardcoded credentials
# api_key = 'your_actual_api_key'  # Never do this!

# Good: Use key rotation
class APIKeyManager:
    def __init__(self):
        self.primary_key = os.getenv('PRIMARY_API_KEY')
        self.backup_key = os.getenv('BACKUP_API_KEY')
        
    def get_active_key(self):
        # Implement key rotation logic
        return self.primary_key
```

### Network Security

```python
# Use secure connections
exchange = ccxt.binance({
    'enableRateLimit': True,
    'timeout': 30000,
    'options': {
        'adjustForTimeDifference': True,
        'recvWindow': 5000,  # Shorter receive window
    }
})

# Implement request signing verification
# Most CCXT exchanges handle this automatically
```

## Performance Optimization

### Efficient Data Management

```python
class EfficientDataManager:
    """Manage data efficiently"""
    
    def __init__(self):
        self.price_cache = {}
        self.cache_expiry = 300  # 5 minutes
        
    def get_price_data(self, symbol: str, force_refresh: bool = False):
        """Get price data with caching"""
        now = datetime.now()
        cache_key = symbol
        
        if (not force_refresh and 
            cache_key in self.price_cache and
            (now - self.price_cache[cache_key]['timestamp']).seconds < self.cache_expiry):
            return self.price_cache[cache_key]['data']
        
        # Fetch fresh data
        data = self.exchange.fetch_ticker(symbol)
        self.price_cache[cache_key] = {
            'data': data,
            'timestamp': now
        }
        
        return data
```

### Memory Management

```python
import gc
from memory_profiler import profile

class MemoryOptimizedStrategy:
    """Strategy with memory optimization"""
    
    def __init__(self):
        self.data_buffer = RingBuffer(100)  # Limited size
        
    def cleanup_old_data(self):
        """Periodic cleanup"""
        # Clear old data
        if hasattr(self, 'old_data'):
            del self.old_data
            
        # Force garbage collection
        gc.collect()
    
    @profile  # Use for memory profiling
    def run_strategy_iteration(self):
        """Memory-profiled strategy iteration"""
        # Your strategy logic here
        pass
```

## Deployment Checklist

### Pre-Deployment

- [ ] All tests pass
- [ ] Configuration validated
- [ ] API keys properly set
- [ ] Risk limits configured
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] Alerts configured
- [ ] Backup procedures in place

### Deployment

- [ ] Deploy to staging first
- [ ] Perform smoke tests
- [ ] Monitor initial trades
- [ ] Verify all systems working
- [ ] Document deployment

### Post-Deployment

- [ ] Monitor performance
- [ ] Check logs regularly
- [ ] Verify trades executing correctly
- [ ] Monitor resource usage
- [ ] Update documentation

## Common Pitfalls to Avoid

1. **Hardcoded Credentials**: Never commit API keys to version control
2. **Insufficient Testing**: Always test thoroughly before going live  
3. **No Risk Management**: Always implement stop losses and position limits
4. **Ignoring Rate Limits**: Respect exchange rate limits
5. **Poor Error Handling**: Handle all possible exceptions
6. **No Monitoring**: Set up comprehensive monitoring and alerting
7. **Overoptimization**: Don't over-optimize on historical data
8. **No Backup Plan**: Have procedures for system failures
9. **Inadequate Logging**: Log all important events for debugging
10. **Manual Interventions**: Automate everything possible

Remember: The goal is consistent, profitable trading with minimal risk. Start small, test thoroughly, and scale gradually. 