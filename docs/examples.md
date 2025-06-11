# Examples

This page provides practical examples of using StratWork to build trading strategies.

## Basic Long Strategy

A simple strategy that buys when price crosses above a moving average:

```python
import ccxt
import time
from stratwork import (
    PositionManager, 
    StopPriceCalculator, 
    TechnicalAnalysisCalculator,
    RingBuffer
)

class SimpleMAStrategy:
    def __init__(self, exchange, symbol='BTC/USDT'):
        self.exchange = exchange
        self.symbol = symbol
        self.price_buffer = RingBuffer(50)
        
        # Position manager setup
        stop_calculator = StopPriceCalculator(stop_loss_pct=2.0)
        self.position_manager = PositionManager(
            long_symbol='BTC',
            short_symbol='USDT',
            max_usd_pos=1000,
            stop_price_calculator=stop_calculator,
            gain_target_pct=3.0,
            exchange=exchange,
            trading=False  # Set to True for live trading
        )
    
    def update_price_data(self):
        """Fetch latest price and update buffer"""
        ticker = self.exchange.fetch_ticker(self.symbol)
        current_price = ticker['last']
        self.price_buffer.add(current_price)
        return current_price
    
    def calculate_signals(self):
        """Calculate trading signals"""
        prices = self.price_buffer.get_all()
        if len(prices) < 20:
            return None
            
        # Calculate moving averages
        sma_10 = TechnicalAnalysisCalculator.sma(prices[-10:])
        sma_20 = TechnicalAnalysisCalculator.sma(prices[-20:])
        current_price = prices[-1]
        
        return {
            'current_price': current_price,
            'sma_10': sma_10,
            'sma_20': sma_20,
            'signal': 'BUY' if sma_10 > sma_20 else 'HOLD'
        }
    
    def run_strategy(self):
        """Main strategy loop"""
        current_price = self.update_price_data()
        signals = self.calculate_signals()
        
        if signals is None:
            print("Insufficient data for signals")
            return
            
        print(f"Price: {current_price:.2f}, SMA10: {signals['sma_10']:.2f}, "
              f"SMA20: {signals['sma_20']:.2f}, Signal: {signals['signal']}")
        
        # Trading logic
        if signals['signal'] == 'BUY' and not self.position_manager.has_active_position():
            print("Opening long position")
            self.position_manager.open_long_position()
        elif self.position_manager.has_active_position():
            print("Position active, monitoring...")

# Usage
exchange = ccxt.binance({
    'apiKey': 'your_api_key',
    'secret': 'your_secret',
    'sandbox': True,
    'enableRateLimit': True,
})

strategy = SimpleMAStrategy(exchange)
strategy.run_strategy()
```

## Mean Reversion Strategy

A strategy that buys when price deviates significantly from the mean:

```python
import numpy as np
from stratwork import PositionManager, StopPriceCalculator, RingBuffer

class MeanReversionStrategy:
    def __init__(self, exchange, symbol='BTC/USDT', lookback=20, std_threshold=2.0):
        self.exchange = exchange
        self.symbol = symbol
        self.lookback = lookback
        self.std_threshold = std_threshold
        self.price_buffer = RingBuffer(lookback * 2)
        
        # Position manager
        stop_calculator = StopPriceCalculator(stop_loss_pct=1.5)
        self.position_manager = PositionManager(
            long_symbol='BTC',
            short_symbol='USDT',
            max_usd_pos=500,
            stop_price_calculator=stop_calculator,
            gain_target_pct=2.0,
            exchange=exchange,
            trading=False
        )
    
    def calculate_bollinger_bands(self):
        """Calculate Bollinger Bands"""
        prices = self.price_buffer.get_all()
        if len(prices) < self.lookback:
            return None
            
        recent_prices = prices[-self.lookback:]
        mean_price = np.mean(recent_prices)
        std_price = np.std(recent_prices)
        
        upper_band = mean_price + (self.std_threshold * std_price)
        lower_band = mean_price - (self.std_threshold * std_price)
        
        return {
            'mean': mean_price,
            'upper': upper_band,
            'lower': lower_band,
            'current': prices[-1]
        }
    
    def run_strategy(self):
        """Execute mean reversion strategy"""
        ticker = self.exchange.fetch_ticker(self.symbol)
        current_price = ticker['last']
        self.price_buffer.add(current_price)
        
        bands = self.calculate_bollinger_bands()
        if bands is None:
            print("Insufficient data for Bollinger Bands")
            return
            
        print(f"Price: {current_price:.2f}, Lower: {bands['lower']:.2f}, "
              f"Upper: {bands['upper']:.2f}")
        
        # Buy when price touches lower band (oversold)
        if (current_price <= bands['lower'] and 
            not self.position_manager.has_active_position()):
            print("Price oversold - Opening long position")
            self.position_manager.open_long_position()
        
        # Sell when price reaches upper band (overbought)
        elif (current_price >= bands['upper'] and 
              self.position_manager.has_active_position()):
            print("Price overbought - Closing position")
            self.position_manager.exit_position()

# Usage
strategy = MeanReversionStrategy(exchange)
strategy.run_strategy()
```

## EMA Crossover Strategy

Strategy based on exponential moving average crossovers:

```python
from stratwork import TechnicalAnalysisCalculator, PositionManager, StopPriceCalculator

class EMACrossoverStrategy:
    def __init__(self, exchange, symbol='BTC/USDT'):
        self.exchange = exchange
        self.symbol = symbol
        self.ema_fast = None  # 12-period EMA
        self.ema_slow = None  # 26-period EMA
        self.previous_signal = None
        
        # Position manager
        stop_calculator = StopPriceCalculator(stop_loss_pct=2.5)
        self.position_manager = PositionManager(
            long_symbol='BTC',
            short_symbol='USDT',
            max_usd_pos=750,
            stop_price_calculator=stop_calculator,
            gain_target_pct=4.0,
            exchange=exchange,
            trading=False
        )
    
    def update_emas(self, price):
        """Update EMA values"""
        self.ema_fast = TechnicalAnalysisCalculator.ema(
            price, self.ema_fast, 12
        )
        self.ema_slow = TechnicalAnalysisCalculator.ema(
            price, self.ema_slow, 26
        )
    
    def get_signal(self):
        """Determine current signal"""
        if self.ema_fast is None or self.ema_slow is None:
            return None
            
        if self.ema_fast > self.ema_slow:
            return 'BUY'
        else:
            return 'SELL'
    
    def run_strategy(self):
        """Execute EMA crossover strategy"""
        ticker = self.exchange.fetch_ticker(self.symbol)
        current_price = ticker['last']
        
        self.update_emas(current_price)
        current_signal = self.get_signal()
        
        if current_signal is None:
            print("Initializing EMAs...")
            return
            
        print(f"Price: {current_price:.2f}, Fast EMA: {self.ema_fast:.2f}, "
              f"Slow EMA: {self.ema_slow:.2f}, Signal: {current_signal}")
        
        # Detect crossover
        if (self.previous_signal == 'SELL' and current_signal == 'BUY' and
            not self.position_manager.has_active_position()):
            print("Bullish crossover - Opening long position")
            self.position_manager.open_long_position()
            
        elif (self.previous_signal == 'BUY' and current_signal == 'SELL' and
              self.position_manager.has_active_position()):
            print("Bearish crossover - Closing position")
            self.position_manager.exit_position()
        
        self.previous_signal = current_signal

# Usage
strategy = EMACrossoverStrategy(exchange)
strategy.run_strategy()
```

## Multi-Timeframe Strategy

Strategy that uses multiple timeframes for confirmation:

```python
import time
from datetime import datetime, timedelta

class MultiTimeframeStrategy:
    def __init__(self, exchange, symbol='BTC/USDT'):
        self.exchange = exchange
        self.symbol = symbol
        
        # Separate buffers for different timeframes
        self.price_buffer_1h = RingBuffer(24)  # 24 hours
        self.price_buffer_4h = RingBuffer(24)  # 4 days
        
        # Position manager
        stop_calculator = StopPriceCalculator(stop_loss_pct=3.0)
        self.position_manager = PositionManager(
            long_symbol='BTC',
            short_symbol='USDT',
            max_usd_pos=1500,
            stop_price_calculator=stop_calculator,
            gain_target_pct=5.0,
            exchange=exchange,
            trading=False
        )
    
    def fetch_ohlcv_data(self, timeframe='1h', limit=50):
        """Fetch OHLCV data for specified timeframe"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(
                self.symbol, timeframe, limit=limit
            )
            return [candle[4] for candle in ohlcv]  # Close prices
        except Exception as e:
            print(f"Error fetching {timeframe} data: {e}")
            return []
    
    def analyze_trend(self, prices, period=14):
        """Simple trend analysis"""
        if len(prices) < period:
            return 'NEUTRAL'
            
        recent_avg = TechnicalAnalysisCalculator.sma(prices[-period//2:])
        older_avg = TechnicalAnalysisCalculator.sma(prices[-period:-period//2])
        
        if recent_avg > older_avg * 1.02:  # 2% threshold
            return 'BULLISH'
        elif recent_avg < older_avg * 0.98:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def run_strategy(self):
        """Execute multi-timeframe strategy"""
        # Fetch data for different timeframes
        prices_1h = self.fetch_ohlcv_data('1h', 50)
        prices_4h = self.fetch_ohlcv_data('4h', 50)
        
        if not prices_1h or not prices_4h:
            print("Insufficient data")
            return
        
        # Analyze trends
        trend_1h = self.analyze_trend(prices_1h)
        trend_4h = self.analyze_trend(prices_4h)
        current_price = prices_1h[-1]
        
        print(f"Price: {current_price:.2f}, 1H Trend: {trend_1h}, 4H Trend: {trend_4h}")
        
        # Trading logic: both timeframes must agree
        if (trend_1h == 'BULLISH' and trend_4h == 'BULLISH' and
            not self.position_manager.has_active_position()):
            print("Multi-timeframe bullish confirmation - Opening long position")
            self.position_manager.open_long_position()
            
        elif (trend_1h == 'BEARISH' and trend_4h == 'BEARISH' and
              self.position_manager.has_active_position()):
            print("Multi-timeframe bearish confirmation - Closing position")
            self.position_manager.exit_position()

# Usage
strategy = MultiTimeframeStrategy(exchange)
strategy.run_strategy()
```

## Running Strategies Continuously

For production use, you'll want to run strategies continuously:

```python
import time
import logging
import schedule

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('strategy.log'),
        logging.StreamHandler()
    ]
)

def run_strategy_safely(strategy_func):
    """Wrapper for safe strategy execution"""
    try:
        strategy_func()
    except Exception as e:
        logging.error(f"Strategy error: {e}")

# Schedule strategy execution
def main():
    exchange = ccxt.binance({
        'apiKey': 'your_api_key',
        'secret': 'your_secret',
        'sandbox': True,
        'enableRateLimit': True,
    })
    
    strategy = SimpleMAStrategy(exchange)
    
    # Schedule strategy to run every 5 minutes
    schedule.every(5).minutes.do(
        run_strategy_safely, 
        strategy.run_strategy
    )
    
    print("Strategy scheduler started...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
```

## Important Notes

1. **Always test in sandbox mode first**
2. **Start with small position sizes**
3. **Monitor your strategies closely**
4. **Implement proper error handling**
5. **Use appropriate stop losses**
6. **Consider market conditions and volatility**

Remember: Past performance doesn't guarantee future results. These examples are for educational purposes only. 