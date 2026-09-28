# ========================================
# تست دقیق تشخیص واگرایی
# ========================================

from data_fetcher import fetch_ohlcv
from rsi_calculator import calculate_rsi
from pivot_detector import detect_pivots, get_pivot_points
import config


def debug_divergence(df, symbol):
    """
    بررسی دقیق چرا واگرایی پیدا نمی‌شه
    """
    df = calculate_rsi(df, period=config.RSI_PERIOD)
    df = detect_pivots(df, left=config.PIVOT_LEFT, right=config.PIVOT_RIGHT)
    
    pivot_highs, pivot_lows = get_pivot_points(df)
    
    print(f"\n{'='*60}")
    print(f"📊 {symbol}")
    print(f"{'='*60}")
    print(f"تعداد پیوت سقف: {len(pivot_highs)}")
    print(f"تعداد پیوت کف: {len(pivot_lows)}")
    
    # بررسی واگرایی صعودی
    if len(pivot_lows) >= 3:
        p1, p2, p3 = pivot_lows[-3], pivot_lows[-2], pivot_lows[-1]
        
        print(f"\n🟢 بررسی واگرایی صعودی (سه پیوت کف آخر):")
        print(f"   P1: قیمت={p1['price']:.4f} | RSI={p1['rsi']:.2f} | index={p1['index']}")
        print(f"   P2: قیمت={p2['price']:.4f} | RSI={p2['rsi']:.2f} | index={p2['index']}")
        print(f"   P3: قیمت={p3['price']:.4f} | RSI={p3['rsi']:.2f} | index={p3['index']}")
        
        dist1 = abs(p2['index'] - p1['index'])
        dist2 = abs(p3['index'] - p2['index'])
        
        print(f"\n   📏 فاصله P1-P2: {dist1} کندل (باید بین 5-25 باشه)")
        print(f"   📏 فاصله P2-P3: {dist2} کندل (باید بین 5-25 باشه)")
        
        rsi_asc = p1['rsi'] < p2['rsi'] < p3['rsi']
        price_desc = p1['price'] > p2['price'] > p3['price']
        
        print(f"\n   ✅ RSI بالارونده: {'✅ بله' if rsi_asc else '❌ خیر'}")
        print(f"   ✅ قیمت پایین‌رونده: {'✅ بله' if price_desc else '❌ خیر'}")
        
        if rsi_asc and price_desc and 5 <= dist1 <= 25 and 5 <= dist2 <= 25:
            print(f"\n   🎯 واگرایی صعودی سه پوش پیدا شد!")
    
    # بررسی واگرایی نزولی
    if len(pivot_highs) >= 3:
        p1, p2, p3 = pivot_highs[-3], pivot_highs[-2], pivot_highs[-1]
        
        print(f"\n🔴 بررسی واگرایی نزولی (سه پیوت سقف آخر):")
        print(f"   P1: قیمت={p1['price']:.4f} | RSI={p1['rsi']:.2f} | index={p1['index']}")
        print(f"   P2: قیمت={p2['price']:.4f} | RSI={p2['rsi']:.2f} | index={p2['index']}")
        print(f"   P3: قیمت={p3['price']:.4f} | RSI={p3['rsi']:.2f} | index={p3['index']}")
        
        dist1 = abs(p2['index'] - p1['index'])
        dist2 = abs(p3['index'] - p2['index'])
        
        print(f"\n   📏 فاصله P1-P2: {dist1} کندل (باید بین 5-25 باشه)")
        print(f"   📏 فاصله P2-P3: {dist2} کندل (باید بین 5-25 باشه)")
        
        rsi_desc = p1['rsi'] > p2['rsi'] > p3['rsi']
        price_asc = p1['price'] < p2['price'] < p3['price']
        
        print(f"\n   ✅ RSI پایین‌رونده: {'✅ بله' if rsi_desc else '❌ خیر'}")
        print(f"   ✅ قیمت بالارونده: {'✅ بله' if price_asc else '❌ خیر'}")
        
        if rsi_desc and price_asc and 5 <= dist1 <= 25 and 5 <= dist2 <= 25:
            print(f"\n   🎯 واگرایی نزولی سه پوش پیدا شد!")


# ===== اجرا =====
if __name__ == "__main__":
    print("🔍 تست دقیق تشخیص واگرایی...")
    
    test_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 
                    'ADA/USDT', 'DOGE/USDT', 'BNB/USDT', 'LTC/USDT',
                    'LINK/USDT', 'DOT/USDT', 'AVAX/USDT', 'MATIC/USDT',
                    'TRX/USDT', 'ATOM/USDT', 'UNI/USDT', 'FIL/USDT',
                    'NEAR/USDT', 'APT/USDT', 'ARB/USDT', 'OP/USDT']
    
    for symbol in test_symbols:
        df = fetch_ohlcv('binance', symbol, '1h', limit=500)
        
        if df is None:
            continue
        
        debug_divergence(df, symbol)
    
    print("\n\n✅ تست تموم شد!")
    print("\n💡 اگه توی هیچ ارزی واگرایی پیدا نشد، طبیعیه.")
    print("   سه پوش واگرایی خیلی نادره و ممکنه هفته‌ها طول بکشه تا یکی پیدا بشه.")