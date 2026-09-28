# ========================================
# Main Scanner — Triple Divergence Bot
# ========================================

import os
import json
import time
from datetime import datetime

import config
from data_fetcher import get_usdt_symbols, fetch_ohlcv
from rsi_calculator import calculate_rsi
from pivot_detector import detect_pivots, get_pivot_points
from divergence_engine import detect_divergence
from chart_generator import generate_divergence_chart
from telegram_bot import send_message, send_photo


# ===== Alert Memory =====
def load_memory():
    if os.path.exists(config.MEMORY_FILE):
        try:
            with open(config.MEMORY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_memory(memory):
    with open(config.MEMORY_FILE, 'w') as f:
        json.dump(memory, f, indent=2)


def make_alert_signature(div, symbol, timeframe):
    p1 = div['price_pivots'][0]['index']
    p2 = div['price_pivots'][1]['index']
    p3 = div['price_pivots'][2]['index']
    
    return f"{symbol}_{timeframe}_{div['type']}_{p1}_{p2}_{p3}"


def cleanup_memory(memory, max_age_hours=48):
    now = time.time()
    cleaned = {}
    
    for key, timestamp in memory.items():
        age_hours = (now - timestamp) / 3600
        if age_hours < max_age_hours:
            cleaned[key] = timestamp
    
    return cleaned


# ===== Scan One Symbol/Timeframe =====
def scan_symbol_timeframe(symbol, timeframe):
    try:
        df = fetch_ohlcv(config.EXCHANGE, symbol, timeframe, limit=config.CANDLE_LIMIT)
        
        if df is None or len(df) < 100:
            return None, []
        
        df = calculate_rsi(df, period=config.RSI_PERIOD)
        df = detect_pivots(df, left=config.PIVOT_LEFT, right=config.PIVOT_RIGHT)
        
        pivots = get_pivot_points(df)
        divergences = detect_divergence(df, pivots)
        
        return df, divergences
    except Exception as e:
        print(f"   Error in {symbol} {timeframe}: {e}")
        return None, []


# ===== Full Scan =====
def scan_all():
    print("\n" + "="*60)
    print(f"Starting scan — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    memory = load_memory()
    memory = cleanup_memory(memory, max_age_hours=48)
    
    symbols = get_usdt_symbols(config.EXCHANGE)
    
    if not symbols:
        print("No symbols found!")
        return
    
    if config.MAX_SYMBOLS > 0:
        symbols = symbols[:config.MAX_SYMBOLS]
    
    print(f"Symbols: {len(symbols)}")
    print(f"Timeframes: {config.TIMEFRAMES}")
    print(f"Memory: {len(memory)} previous alerts")
    print("-"*60)
    
    new_alerts = 0
    total_scanned = 0
    
    for i, symbol in enumerate(symbols):
        for tf in config.TIMEFRAMES:
            total_scanned += 1
            
            try:
                df, divergences = scan_symbol_timeframe(symbol, tf)
                
                if df is None or not divergences:
                    continue
                
                for div in divergences:
                    signature = make_alert_signature(div, symbol, tf)
                    
                    if signature in memory:
                        continue
                    
                    print(f"\nNEW: {symbol} {tf} — {div['label']} ({div['candles_ago']} candles ago)")
                    
                    # Chart
                    chart_path = f"alerts/{symbol.replace('/', '_')}_{tf}.png"
                    os.makedirs('alerts', exist_ok=True)
                    
                    chart_result = generate_divergence_chart(
                        df, div, symbol, tf, chart_path
                    )
                    
                    # English caption
                    caption = (
                        f"<b>{symbol}</b> — <b>{tf}</b>\n"
                        f"<b>{div['label']}</b>\n"
                        f"Candles ago: {div['candles_ago']}\n\n"
                        f"<b>Price Pivots:</b>\n"
                        f"  • {div['price_values'][0]:.6f}\n"
                        f"  • {div['price_values'][1]:.6f}\n"
                        f"  • {div['price_values'][2]:.6f}\n\n"
                        f"<b>RSI Pivots:</b>\n"
                        f"  • {div['rsi_values'][0]:.2f}\n"
                        f"  • {div['rsi_values'][1]:.2f}\n"
                        f"  • {div['rsi_values'][2]:.2f}"
                    )
                    
                    # Send
                    if chart_result and os.path.exists(chart_result):
                        send_photo(chart_result, caption)
                    else:
                        send_message(caption)
                    
                    memory[signature] = time.time()
                    save_memory(memory)
                    
                    new_alerts += 1
            except Exception as e:
                print(f"   Error in {symbol} {tf}: {e}")
                continue
        
        if (i + 1) % 20 == 0:
            print(f"   Progress: {i+1}/{len(symbols)} — {new_alerts} new alerts")
    
    save_memory(memory)
    
    print("\n" + "="*60)
    print(f"Scan complete")
    print(f"   Total scanned: {total_scanned}")
    print(f"   New alerts: {new_alerts}")
    print("="*60)


# ===== Main Loop =====
def main():
    print("="*60)
    print("Triple Divergence Bot — Scanner")
    print("="*60)
    print(f"Scan interval: {config.SCAN_INTERVAL_SECONDS}s")
    print(f"MAX_CANDLES_AGO = {config.MAX_CANDLES_AGO}")
    print("="*60)
    
    send_message(
        f"<b>Triple Divergence Bot Started</b>\n\n"
        f"Scan interval: {config.SCAN_INTERVAL_SECONDS // 60} min\n"
        f"Timeframes: {', '.join(config.TIMEFRAMES)}\n"
        f"Filter: only fresh divergences (≤{config.MAX_CANDLES_AGO} candles)"
    )
    
    while True:
        try:
            scan_all()
        except Exception as e:
            print(f"Main loop error: {e}")
            import traceback
            traceback.print_exc()
        
        print(f"\nSleeping {config.SCAN_INTERVAL_SECONDS}s...\n")
        time.sleep(config.SCAN_INTERVAL_SECONDS)


if __name__ == "__main__":
    main()