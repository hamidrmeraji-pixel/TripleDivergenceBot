# تست با یک مورد شناخته‌شده
from data_fetcher import fetch_ohlcv
from rsi_calculator import calculate_rsi
from pivot_detector import detect_pivots, get_pivot_points
from divergence_engine import detect_divergence
import config

# تست روی ۵۰ ارز
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT', 
           'DOGE/USDT', 'BNB/USDT', 'LTC/USDT', 'LINK/USDT', 'DOT/USDT',
           'AVAX/USDT', 'MATIC/USDT', 'TRX/USDT', 'ATOM/USDT', 'UNI/USDT',
           'FIL/USDT', 'NEAR/USDT', 'APT/USDT', 'ARB/USDT', 'OP/USDT',
           'INJ/USDT', 'SUI/USDT', 'SEI/USDT', 'TIA/USDT', 'RUNE/USDT',
           'AAVE/USDT', 'MKR/USDT', 'CRV/USDT', 'SAND/USDT', 'MANA/USDT',
           'GALA/USDT', 'IMX/USDT', 'FTM/USDT', 'ALGO/USDT', 'VET/USDT',
           'EGLD/USDT', 'THETA/USDT', 'AXS/USDT', 'EOS/USDT', 'XTZ/USDT']

total = 0

for symbol in symbols:
    try:
        df = fetch_ohlcv('binance', symbol, '1h', limit=1000)
        
        if df is None:
            continue
        
        df = calculate_rsi(df, period=config.RSI_PERIOD)
        df = detect_pivots(df, left=config.PIVOT_LEFT, right=config.PIVOT_RIGHT)
        
        pivot_highs, pivot_lows = get_pivot_points(df)
        divergences = detect_divergence(df, pivot_highs, pivot_lows)
        
        if divergences:
            print(f"\n✅ {symbol}: {len(divergences)} واگرایی")
            for div in divergences[:2]:
                print(f"   {div['label']}")
                print(f"   قیمت: {[f'{p:.4f}' for p in div['price_values']]}")
                print(f"   RSI: {[f'{p:.2f}' for p in div['rsi_values']]}")
            total += len(divergences)
    except Exception as e:
        print(f"❌ {symbol}: {e}")

print(f"\n\n📊 مجموع: {total} واگرایی")