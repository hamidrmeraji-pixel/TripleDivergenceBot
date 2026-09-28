# ========================================
# تشخیص پیوت‌های ماژور (نسخه اصلاح‌شده)
# ========================================

import pandas as pd
import numpy as np
import config


def detect_pivots_on_series(series, left=3, right=3, mode='high'):
    """
    تشخیص پیوت روی یک سری داده (قیمت یا RSI)
    
    mode: 'high' برای سقف، 'low' برای کف
    """
    pivot_flags = [False] * len(series)
    
    for i in range(left, len(series) - right):
        value = series.iloc[i]
        
        if mode == 'high':
            is_pivot = True
            for j in range(1, left + 1):
                if value <= series.iloc[i - j]:
                    is_pivot = False
                    break
            if is_pivot:
                for j in range(1, right + 1):
                    if value <= series.iloc[i + j]:
                        is_pivot = False
                        break
            if is_pivot:
                pivot_flags[i] = True
        
        else:  # low
            is_pivot = True
            for j in range(1, left + 1):
                if value >= series.iloc[i - j]:
                    is_pivot = False
                    break
            if is_pivot:
                for j in range(1, right + 1):
                    if value >= series.iloc[i + j]:
                        is_pivot = False
                        break
            if is_pivot:
                pivot_flags[i] = True
    
    return pivot_flags


def detect_pivots(df, left=3, right=3):
    """
    تشخیص پیوت‌ها روی قیمت و RSI به صورت جداگانه
    """
    # پیوت روی قیمت
    df['pivot_high'] = detect_pivots_on_series(df['high'], left, right, 'high')
    df['pivot_low'] = detect_pivots_on_series(df['low'], left, right, 'low')
    
    # پیوت روی RSI
    df['rsi_pivot_high'] = detect_pivots_on_series(df['rsi'], left, right, 'high')
    df['rsi_pivot_low'] = detect_pivots_on_series(df['rsi'], left, right, 'low')
    
    return df


def get_pivot_points(df):
    """
    استخراج لیست پیوت‌های قیمت و RSI
    """
    # پیوت‌های قیمت
    price_pivot_highs = []
    price_pivot_lows = []
    
    for i in range(len(df)):
        if df['pivot_high'].iloc[i]:
            price_pivot_highs.append({
                'index': i,
                'price': df['high'].iloc[i],
                'rsi': df['rsi'].iloc[i],
                'datetime': df['datetime'].iloc[i]
            })
        
        if df['pivot_low'].iloc[i]:
            price_pivot_lows.append({
                'index': i,
                'price': df['low'].iloc[i],
                'rsi': df['rsi'].iloc[i],
                'datetime': df['datetime'].iloc[i]
            })
    
    # پیوت‌های RSI
    rsi_pivot_highs = []
    rsi_pivot_lows = []
    
    for i in range(len(df)):
        if df['rsi_pivot_high'].iloc[i]:
            rsi_pivot_highs.append({
                'index': i,
                'price': df['close'].iloc[i],
                'rsi': df['rsi'].iloc[i],
                'datetime': df['datetime'].iloc[i]
            })
        
        if df['rsi_pivot_low'].iloc[i]:
            rsi_pivot_lows.append({
                'index': i,
                'price': df['close'].iloc[i],
                'rsi': df['rsi'].iloc[i],
                'datetime': df['datetime'].iloc[i]
            })
    
    return {
        'price_pivot_highs': price_pivot_highs,
        'price_pivot_lows': price_pivot_lows,
        'rsi_pivot_highs': rsi_pivot_highs,
        'rsi_pivot_lows': rsi_pivot_lows
    }


# ===== تست =====
if __name__ == "__main__":
    from data_fetcher import fetch_ohlcv
    from rsi_calculator import calculate_rsi
    
    print("🔍 تست تشخیص پیوت‌ها (نسخه اصلاح‌شده)...")
    print("-" * 50)
    
    df = fetch_ohlcv('binance', 'ADA/USDT', '1h', limit=200)
    
    if df is not None:
        df = calculate_rsi(df, period=config.RSI_PERIOD)
        df = detect_pivots(df, left=config.PIVOT_LEFT, right=config.PIVOT_RIGHT)
        
        pivots = get_pivot_points(df)
        
        print(f"\n📈 پیوت سقف قیمت: {len(pivots['price_pivot_highs'])}")
        print(f"📉 پیوت کف قیمت: {len(pivots['price_pivot_lows'])}")
        print(f"📈 پیوت سقف RSI: {len(pivots['rsi_pivot_highs'])}")
        print(f"📉 پیوت کف RSI: {len(pivots['rsi_pivot_lows'])}")
        
        print(f"\n۵ پیوت کف قیمت آخر:")
        for p in pivots['price_pivot_lows'][-5:]:
            print(f"   index={p['index']} — قیمت={p['price']:.4f} — RSI={p['rsi']:.2f}")
        
        print(f"\n۵ پیوت کف RSI آخر:")
        for p in pivots['rsi_pivot_lows'][-5:]:
            print(f"   index={p['index']} — قیمت={p['price']:.4f} — RSI={p['rsi']:.2f}")