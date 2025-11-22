def calculate_signals(df):
    signals = []
    
    # RSI
    if 'RSI' in df.columns:
        current_rsi = df['RSI'].iloc[-1]
        if current_rsi < 30:
            signals.append(("🟢", "Oversold (RSI < 30)", "Potential Buy"))
        elif current_rsi > 70:
            signals.append(("🔴", "Overbought (RSI > 70)", "Potential Sell"))
        
    # MACD
    if 'MACD_12_26_9' in df.columns and 'MACDs_12_26_9' in df.columns:
        macd = df['MACD_12_26_9'].iloc[-1]
        signal = df['MACDs_12_26_9'].iloc[-1]
        prev_macd = df['MACD_12_26_9'].iloc[-2]
        prev_signal = df['MACDs_12_26_9'].iloc[-2]
        
        if prev_macd < prev_signal and macd > signal:
            signals.append(("🟢", "MACD Bullish Crossover", "Momentum Shift Up"))
        elif prev_macd > prev_signal and macd < signal:
            signals.append(("🔴", "MACD Bearish Crossover", "Momentum Shift Down"))
        
    # SMA Crossover (Golden/Death Cross)
    if 'SMA_50' in df.columns and 'SMA_200' in df.columns:
        sma50 = df['SMA_50'].iloc[-1]
        sma200 = df['SMA_200'].iloc[-1]
        prev_sma50 = df['SMA_50'].iloc[-2]
        prev_sma200 = df['SMA_200'].iloc[-2]
        
        if prev_sma50 < prev_sma200 and sma50 > sma200:
            signals.append(("⭐", "Golden Cross (50 > 200)", "Strong Bullish Signal"))
        elif prev_sma50 > prev_sma200 and sma50 < sma200:
            signals.append(("💀", "Death Cross (50 < 200)", "Strong Bearish Signal"))
            
    return signals
