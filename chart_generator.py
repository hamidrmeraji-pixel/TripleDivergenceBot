# ========================================
# Chart Generator — TradingView Style
# ========================================

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
import os


# ===== TradingView Colors =====
BG_COLOR = '#131722'
GRID_COLOR = '#1e222d'
TEXT_COLOR = '#d1d4dc'
GREEN = '#26a69a'
RED = '#ef5350'
RSI_COLOR = '#7e57c2'
RSI_BAND = '#787b86'
WICK_GREEN = '#26a69a'
WICK_RED = '#ef5350'


def generate_divergence_chart(df, divergence, symbol, timeframe, output_path='chart.png'):
    """
    Create TradingView-style chart with triple divergence
    """
    try:
        price_pivots = divergence['price_pivots']
        rsi_pivots = divergence['rsi_pivots']
        div_type = divergence['type']
        
        if div_type == 'BULLISH':
            arrow_color = GREEN
            title_color = GREEN
        else:
            arrow_color = RED
            title_color = RED
        
        # Visible range
        all_indices = [p['index'] for p in price_pivots] + [p['index'] for p in rsi_pivots]
        first_idx = min(all_indices)
        last_idx = max(all_indices)
        
        start_idx = max(0, first_idx - 25)
        end_idx = min(len(df) - 1, last_idx + 20)
        
        visible_df = df.iloc[start_idx:end_idx + 1].reset_index(drop=True)
        
        # ===== Figure: Price taller but RSI bigger =====
        fig = plt.figure(figsize=(16, 11))
        fig.patch.set_facecolor(BG_COLOR)
        
        # Grid: Price (top 60%), RSI (bottom 40%)
        gs = fig.add_gridspec(2, 1, height_ratios=[1.6, 1.0], hspace=0.05)
        ax1 = fig.add_subplot(gs[0])
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        
        ax1.set_facecolor(BG_COLOR)
        ax2.set_facecolor(BG_COLOR)
        
        # ===== Price Candlesticks =====
        for i in range(len(visible_df)):
            row = visible_df.iloc[i]
            is_green = row['close'] >= row['open']
            candle_color = GREEN if is_green else RED
            
            # Wick
            ax1.plot([i, i], [row['low'], row['high']],
                    color=candle_color, linewidth=1.0, zorder=2)
            
            # Body
            body_low = min(row['open'], row['close'])
            body_high = max(row['open'], row['close'])
            body_height = body_high - body_low
            
            # Minimum body height for visibility
            min_body = row['close'] * 0.0008
            if body_height < min_body:
                body_low = row['close'] - min_body / 2
                body_high = row['close'] + min_body / 2
            
            ax1.plot([i, i], [body_low, body_high],
                    color=candle_color, linewidth=6, alpha=1.0,
                    solid_capstyle='butt', zorder=3)
        
        # Log scale
        ax1.set_yscale('log')
        
        # ===== Price Pivots =====
        price_pivot_x = []
        price_pivot_y = []
        
        for p in price_pivots:
            x = p['index'] - start_idx
            if 0 <= x < len(visible_df):
                price_pivot_x.append(x)
                price_pivot_y.append(p['price'])
                
                # Circle
                ax1.scatter(x, p['price'], color=arrow_color, s=180,
                           marker='o', facecolors='none',
                           linewidths=2, zorder=5)
        
        # Connection line
        if len(price_pivot_x) >= 2:
            ax1.plot(price_pivot_x, price_pivot_y, color=arrow_color,
                    linewidth=2, linestyle='--', alpha=0.85, zorder=4)
        
        # ===== Arrow on 3rd pivot =====
        last_price_pivot = price_pivots[-1]
        x_arrow = last_price_pivot['index'] - start_idx
        
        if 0 <= x_arrow < len(visible_df):
            y_arrow = last_price_pivot['price']
            
            if div_type == 'BULLISH':
                offset = y_arrow * 0.04
                ax1.scatter(x_arrow, y_arrow - offset,
                           color=arrow_color, s=500,
                           marker='^', zorder=10,
                           edgecolors='white', linewidths=1.2)
            else:
                offset = y_arrow * 0.04
                ax1.scatter(x_arrow, y_arrow + offset,
                           color=arrow_color, s=500,
                           marker='v', zorder=10,
                           edgecolors='white', linewidths=1.2)
        
        # ===== RSI =====
        rsi_data = visible_df['rsi'].values
        x_axis = np.arange(len(visible_df))
        
        # RSI bands
        ax2.axhspan(30, 70, color=RSI_BAND, alpha=0.08)
        ax2.axhline(70, color=RSI_BAND, linestyle='--', linewidth=0.8, alpha=0.5)
        ax2.axhline(30, color=RSI_BAND, linestyle='--', linewidth=0.8, alpha=0.5)
        ax2.axhline(50, color=RSI_BAND, linestyle=':', linewidth=0.5, alpha=0.3)
        
        ax2.plot(x_axis, rsi_data, color=RSI_COLOR, linewidth=2.0, zorder=3)
        
        # ===== RSI Pivots =====
        rsi_pivot_x = []
        rsi_pivot_y = []
        
        for p in rsi_pivots:
            x = p['index'] - start_idx
            if 0 <= x < len(visible_df):
                rsi_pivot_x.append(x)
                rsi_pivot_y.append(p['rsi'])
                
                ax2.scatter(x, p['rsi'], color=arrow_color, s=180,
                           marker='o', facecolors='none',
                           linewidths=2, zorder=5)
        
        if len(rsi_pivot_x) >= 2:
            ax2.plot(rsi_pivot_x, rsi_pivot_y, color=arrow_color,
                    linewidth=2, linestyle='--', alpha=0.85, zorder=4)
        
        # ===== Title (English) =====
        title_text = f"{symbol}  |  {timeframe}  |  {divergence['label']}"
        ax1.set_title(title_text, fontsize=15, fontweight='bold',
                     color=title_color, loc='left', pad=12)
        
        # ===== Axis styling =====
        ax1.tick_params(colors=TEXT_COLOR, labelsize=10)
        ax1.set_ylabel('Price', fontsize=11, color=TEXT_COLOR)
        ax1.grid(True, alpha=0.12, color=GRID_COLOR, linewidth=0.5)
        
        for spine in ax1.spines.values():
            spine.set_color(GRID_COLOR)
        
        ax1.yaxis.set_major_formatter(mticker.ScalarFormatter())
        ax1.yaxis.set_minor_formatter(mticker.NullFormatter())
        ax1.ticklabel_format(style='plain', axis='y')
        
        ax2.tick_params(colors=TEXT_COLOR, labelsize=10)
        ax2.set_ylabel('RSI (14)', fontsize=11, color=TEXT_COLOR)
        ax2.set_xlabel('Candles', fontsize=11, color=TEXT_COLOR)
        ax2.grid(True, alpha=0.12, color=GRID_COLOR, linewidth=0.5)
        ax2.set_ylim(0, 100)
        ax2.set_yticks([0, 20, 30, 50, 70, 80, 100])
        
        for spine in ax2.spines.values():
            spine.set_color(GRID_COLOR)
        
        # Hide x labels on top chart
        ax1.set_xticklabels([])
        
        plt.savefig(output_path, dpi=120, bbox_inches='tight',
                   facecolor=BG_COLOR)
        plt.close()
        
        return output_path
    
    except Exception as e:
        print(f"Error creating chart: {e}")
        import traceback
        traceback.print_exc()
        return None


def generate_chart_from_symbol(divergence, symbol, timeframe, output_path='chart.png'):
    """
    Helper that fetches data internally
    """
    from data_fetcher import fetch_ohlcv
    from rsi_calculator import calculate_rsi
    from pivot_detector import detect_pivots
    import config
    
    df = fetch_ohlcv('binance', symbol, timeframe, limit=1000)
    
    if df is None:
        return None
    
    df = calculate_rsi(df, period=14)
    df = detect_pivots(df, left=3, right=3)
    
    return generate_divergence_chart(df, divergence, symbol, timeframe, output_path)


# ===== Test =====
if __name__ == "__main__":
    from data_fetcher import fetch_ohlcv
    from rsi_calculator import calculate_rsi
    from pivot_detector import detect_pivots, get_pivot_points
    from divergence_engine import detect_divergence
    import config
    
    print("Testing chart generation...")
    print("-" * 50)
    
    os.makedirs('test_charts', exist_ok=True)
    
    test_symbols = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'SOL/USDT',
                    'ADA/USDT', 'BNB/USDT', 'DOGE/USDT', 'LTC/USDT',
                    'LINK/USDT', 'AVAX/USDT', 'ARB/USDT', 'OP/USDT',
                    'NEAR/USDT', 'ATOM/USDT', 'UNI/USDT', 'FIL/USDT']
    
    total_charts = 0
    
    for symbol in test_symbols:
        for tf in ['15m', '1h', '4h']:
            df = fetch_ohlcv('binance', symbol, tf, limit=1000)
            
            if df is None:
                continue
            
            df = calculate_rsi(df, period=config.RSI_PERIOD)
            df = detect_pivots(df, left=config.PIVOT_LEFT, right=config.PIVOT_RIGHT)
            
            pivots = get_pivot_points(df)
            divergences = detect_divergence(df, pivots)
            
            if divergences:
                div = divergences[0]
                print(f"{symbol} {tf}: {div['label']} — {div['candles_ago']} candles ago")
                
                filename = f"test_charts/{symbol.replace('/', '_')}_{tf}.png"
                result = generate_divergence_chart(df, div, symbol, tf, filename)
                
                if result:
                    total_charts += 1
    
    print(f"\n{total_charts} charts saved to test_charts/")