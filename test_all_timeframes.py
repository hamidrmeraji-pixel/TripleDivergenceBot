# ========================================
# تست همه تایم‌فریم‌ها + دیباگ
# ========================================

from data_fetcher import fetch_ohlcv
from rsi_calculator import calculate_rsi
from pivot_detector import detect_pivots, get_pivot_points
import divergence_engine
import config


def test_symbol_timeframe(symbol, timeframe):
    """
    تست یک ارز در یک تایم‌فریم
    """
    df = fetch_ohlcv('binance', symbol, timeframe, limit=1000)
    
    if df is None:
        return 0, 0, 0
    
    df = calculate_rsi(df, period=config.RSI_PERIOD)
    df = detect_pivots(df, left=config.PIVOT_LEFT, right=config.PIVOT_RIGHT)
    
    pivots = get_pivot_points(df)
    
    # همه واگرایی‌ها (بدون فیلتر)
    all_divs = []
    all_divs.extend(divergence_engine.detect_bullish_triple_divergence(
        pivots['price_pivot_lows'], pivots['rsi_pivot_lows']))
    all_divs.extend(divergence_engine.detect_bearish_triple_divergence(
        pivots['price_pivot_highs'], pivots['rsi_pivot_highs']))
    
    # واگرایی‌های جدید (با فیلتر)
    last_idx = len(df) - 1
    fresh_divs = []
    
    for div in all_divs:
        candles_ago = last_idx - div['last_pivot_index']
        if candles_ago <= config.MAX_CANDLES_AGO:
            div['candles_ago'] = candles_ago
            fresh_divs.append(div)
    
    # جدیدترین واگرایی (حتی اگه قدیمی باشه) برای دیباگ
    if all_divs:
        all_divs.sort(key=lambda x: x['last_pivot_index'], reverse=True)
        newest = all_divs[0]
        newest_ago = last_idx - newest['last_pivot_index']
    else:
        newest_ago = None
    
    return len(all_divs), len(fresh_divs), newest_ago


# ===== اجرای تست =====
if __name__ == "__main__":
    print("🔍 تست همه تایم‌فریم‌ها")
    print(f"📌 MAX_CANDLES_AGO = {config.MAX_CANDLES_AGO}")
    print("=" * 70)
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT',
               'DOGE/USDT', 'BNB/USDT', 'LTC/USDT', 'LINK/USDT', 'AVAX/USDT',
               'ARB/USDT', 'OP/USDT', 'NEAR/USDT', 'ATOM/USDT', 'UNI/USDT',
               'FIL/USDT', 'INJ/USDT', 'SUI/USDT', 'TIA/USDT', 'SEI/USDT',
               'PEPE/USDT', 'WIF/USDT', 'BONK/USDT', 'FLOKI/USDT', 'SHIB/USDT']
    
    timeframes = ['15m', '1h', '4h']
    
    grand_total_all = 0
    grand_total_fresh = 0
    
    for tf in timeframes:
        print(f"\n{'='*70}")
        print(f"⏱️  تایم‌فریم: {tf}")
        print(f"{'='*70}")
        
        tf_total_all = 0
        tf_total_fresh = 0
        
        for symbol in symbols:
            try:
                total_all, total_fresh, newest_ago = test_symbol_timeframe(symbol, tf)
                
                tf_total_all += total_all
                tf_total_fresh += total_fresh
                
                if total_all > 0:
                    status = f"کل: {total_all}"
                    if total_fresh > 0:
                        status += f" | جدید: {total_fresh} ✅"
                    else:
                        status += f" | جدید: 0 (جدیدترین: {newest_ago} کندل پیش)"
                    print(f"   📊 {symbol}: {status}")
            except Exception as e:
                print(f"   ❌ {symbol}: {e}")
        
        print(f"\n   📈 جمع {tf}: کل={tf_total_all} | جدید={tf_total_fresh}")
        
        grand_total_all += tf_total_all
        grand_total_fresh += tf_total_fresh
    
    print(f"\n{'='*70}")
    print(f"🎯 نتیجه نهایی:")
    print(f"   کل واگرایی‌ها: {grand_total_all}")
    print(f"   واگرایی‌های جدید (≤{config.MAX_CANDLES_AGO} کندل): {grand_total_fresh}")
    print(f"{'='*70}")