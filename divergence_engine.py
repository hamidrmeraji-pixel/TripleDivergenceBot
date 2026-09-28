# ========================================
# Triple Divergence Engine (English Labels)
# ========================================

import config


def check_distance_constraint(pivot1, pivot2):
    distance = abs(pivot2['index'] - pivot1['index'])
    return config.MIN_PIVOT_DISTANCE <= distance <= config.MAX_PIVOT_DISTANCE


def find_nearest_rsi_pivot(price_pivot, rsi_pivots, max_distance=5):
    best_match = None
    best_distance = max_distance + 1
    
    for rsi_p in rsi_pivots:
        distance = abs(rsi_p['index'] - price_pivot['index'])
        if distance < best_distance:
            best_distance = distance
            best_match = rsi_p
    
    if best_match and best_distance <= max_distance:
        return best_match
    return None


def detect_bullish_triple_divergence(price_pivot_lows, rsi_pivot_lows):
    if len(price_pivot_lows) < 3:
        return []
    
    results = []
    
    for i in range(len(price_pivot_lows) - 2):
        p_price_1 = price_pivot_lows[i]
        p_price_2 = price_pivot_lows[i + 1]
        p_price_3 = price_pivot_lows[i + 2]
        
        if not check_distance_constraint(p_price_1, p_price_2):
            continue
        if not check_distance_constraint(p_price_2, p_price_3):
            continue
        
        p_rsi_1 = find_nearest_rsi_pivot(p_price_1, rsi_pivot_lows)
        p_rsi_2 = find_nearest_rsi_pivot(p_price_2, rsi_pivot_lows)
        p_rsi_3 = find_nearest_rsi_pivot(p_price_3, rsi_pivot_lows)
        
        if not (p_rsi_1 and p_rsi_2 and p_rsi_3):
            continue
        
        price_descending = (p_price_1['price'] > p_price_2['price'] > p_price_3['price'])
        rsi_ascending = (p_rsi_1['rsi'] < p_rsi_2['rsi'] < p_rsi_3['rsi'])
        
        if price_descending and rsi_ascending:
            results.append({
                'type': 'BULLISH',
                'label': 'Bullish Triple Divergence',
                'price_pivots': [p_price_1, p_price_2, p_price_3],
                'rsi_pivots': [p_rsi_1, p_rsi_2, p_rsi_3],
                'price_values': [p_price_1['price'], p_price_2['price'], p_price_3['price']],
                'rsi_values': [p_rsi_1['rsi'], p_rsi_2['rsi'], p_rsi_3['rsi']],
                'last_pivot_index': p_price_3['index']
            })
    
    return results


def detect_bearish_triple_divergence(price_pivot_highs, rsi_pivot_highs):
    if len(price_pivot_highs) < 3:
        return []
    
    results = []
    
    for i in range(len(price_pivot_highs) - 2):
        p_price_1 = price_pivot_highs[i]
        p_price_2 = price_pivot_highs[i + 1]
        p_price_3 = price_pivot_highs[i + 2]
        
        if not check_distance_constraint(p_price_1, p_price_2):
            continue
        if not check_distance_constraint(p_price_2, p_price_3):
            continue
        
        p_rsi_1 = find_nearest_rsi_pivot(p_price_1, rsi_pivot_highs)
        p_rsi_2 = find_nearest_rsi_pivot(p_price_2, rsi_pivot_highs)
        p_rsi_3 = find_nearest_rsi_pivot(p_price_3, rsi_pivot_highs)
        
        if not (p_rsi_1 and p_rsi_2 and p_rsi_3):
            continue
        
        price_ascending = (p_price_1['price'] < p_price_2['price'] < p_price_3['price'])
        rsi_descending = (p_rsi_1['rsi'] > p_rsi_2['rsi'] > p_rsi_3['rsi'])
        
        if price_ascending and rsi_descending:
            results.append({
                'type': 'BEARISH',
                'label': 'Bearish Triple Divergence',
                'price_pivots': [p_price_1, p_price_2, p_price_3],
                'rsi_pivots': [p_rsi_1, p_rsi_2, p_rsi_3],
                'price_values': [p_price_1['price'], p_price_2['price'], p_price_3['price']],
                'rsi_values': [p_rsi_1['rsi'], p_rsi_2['rsi'], p_rsi_3['rsi']],
                'last_pivot_index': p_price_3['index']
            })
    
    return results


def detect_divergence(df, pivots):
    divergences = []
    
    bullish = detect_bullish_triple_divergence(
        pivots['price_pivot_lows'],
        pivots['rsi_pivot_lows']
    )
    divergences.extend(bullish)
    
    bearish = detect_bearish_triple_divergence(
        pivots['price_pivot_highs'],
        pivots['rsi_pivot_highs']
    )
    divergences.extend(bearish)
    
    last_candle_index = len(df) - 1
    fresh_divergences = []
    
    for div in divergences:
        candles_ago = last_candle_index - div['last_pivot_index']
        
        if candles_ago <= config.MAX_CANDLES_AGO:
            div['candles_ago'] = candles_ago
            fresh_divergences.append(div)
    
    fresh_divergences.sort(key=lambda x: x['last_pivot_index'], reverse=True)
    
    return fresh_divergences


if __name__ == "__main__":
    from data_fetcher import fetch_ohlcv
    from rsi_calculator import calculate_rsi
    from pivot_detector import detect_pivots, get_pivot_points
    
    print("Testing Triple Divergence Engine...")
    print("-" * 50)
    
    symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'ADA/USDT']
    
    for symbol in symbols:
        df = fetch_ohlcv('binance', symbol, '1h', limit=1000)
        if df is None:
            continue
        
        df = calculate_rsi(df, period=config.RSI_PERIOD)
        df = detect_pivots(df, left=config.PIVOT_LEFT, right=config.PIVOT_RIGHT)
        
        pivots = get_pivot_points(df)
        divergences = detect_divergence(df, pivots)
        
        if divergences:
            print(f"\n{symbol}: {len(divergences)} new divergence(s)")
            for div in divergences[:2]:
                print(f"   {div['label']} — {div['candles_ago']} candles ago")
        else:
            print(f"{symbol}: no new divergence")