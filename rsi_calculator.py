# ========================================
# محاسبه RSI
# ========================================

import pandas as pd
import numpy as np
import config


def calculate_rsi(df, period=14):
    """
    محاسبه RSI با روش استاندارد (Wilder's Smoothing)
    """
    delta = df['close'].diff()
    
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # میانگین متحرک نمایی (روش وایلدر)
    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    df['rsi'] = rsi
    
    return df


# ===== تست =====
if __name__ == "__main__":
    from data_fetcher import fetch_ohlcv
    
    print("🔍 تست محاسبه RSI...")
    print("-" * 50)
    
    # دریافت دیتا
    df = fetch_ohlcv('binance', 'BTC/USDT', '1h', limit=100)
    
    if df is not None:
        # محاسبه RSI
        df = calculate_rsi(df, period=config.RSI_PERIOD)
        
        print(f"✅ RSI محاسبه شد.")
        print(f"\n۵ کندل آخر با RSI:")
        print(df[['datetime', 'close', 'rsi']].tail())
    else:
        print("❌ خطا در دریافت دیتا!")