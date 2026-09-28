# ========================================
# دریافت دیتا از صرافی‌ها
# ========================================

import ccxt
import pandas as pd
from datetime import datetime
import config


def get_exchange(exchange_name='binance'):
    """
    ساخت اتصال به صرافی
    """
    exchange_class = getattr(ccxt, exchange_name)
    exchange = exchange_class({
        'enableRateLimit': True,  # جلوگیری از بلاک شدن
        'options': {
            'defaultType': 'spot',  # فقط اسپات
        }
    })
    return exchange


def fetch_ohlcv(exchange_name, symbol, timeframe, limit=300):
    """
    دریافت کندل‌های قیمتی از صرافی
    
    خروجی: یک DataFrame با ستون‌های:
    timestamp, open, high, low, close, volume
    """
    try:
        exchange = get_exchange(exchange_name)
        
        # دریافت داده
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        
        if not ohlcv:
            return None
        
        # تبدیل به DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # تبدیل timestamp به تاریخ خوانا
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        return df
    
    except Exception as e:
        print(f"❌ خطا در دریافت {symbol} از {exchange_name}: {e}")
        return None


def get_usdt_symbols(exchange_name='binance'):
    """
    دریافت لیست تمام جفت‌ارزهای USDT در صرافی
    """
    try:
        exchange = get_exchange(exchange_name)
        markets = exchange.load_markets()
        
        symbols = []
        for symbol, market in markets.items():
            if market['spot'] and market['quote'] == 'USDT' and market['active']:
                symbols.append(symbol)
        
        return symbols
    
    except Exception as e:
        print(f"❌ خطا در دریافت لیست ارزها: {e}")
        return []


# ===== تست =====
if __name__ == "__main__":
    print("🔍 تست دریافت دیتا از Binance...")
    print("-" * 50)
    
    # تست ۱: دریافت دیتای BTC/USDT
    print("\n۱️⃣ دریافت BTC/USDT در تایم‌فریم ۱ ساعته...")
    df = fetch_ohlcv('binance', 'BTC/USDT', '1h', limit=10)
    
    if df is not None:
        print(f"✅ {len(df)} کندل دریافت شد.")
        print("\n۵ کندل آخر:")
        print(df[['datetime', 'open', 'high', 'low', 'close']].tail())
    else:
        print("❌ خطا در دریافت دیتا!")
    
    # تست ۲: دریافت لیست ارزها
    print("\n" + "-" * 50)
    print("\n۲️⃣ دریافت لیست جفت‌ارزهای USDT...")
    symbols = get_usdt_symbols('binance')
    
    if symbols:
        print(f"✅ {len(symbols)} جفت‌ارز USDT پیدا شد.")
        print(f"\n۱۰ تای اول: {symbols[:10]}")
    else:
        print("❌ خطا در دریافت لیست ارزها!")
    
    print("\n✅ تست تموم شد!")