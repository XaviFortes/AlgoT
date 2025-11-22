import streamlit as st
import yfinance as yf
import pandas_ta as ta
from prophet import Prophet
from prophet.plot import plot_plotly
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="ProTrade Analytics", page_icon="📈")

# --- CUSTOM CSS (Professional Dark Theme) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .metric-card {
        background-color: #1e2127;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .news-card {
        background-color: #1e2127;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 5px;
    }
    h1, h2, h3 {
        font-family: 'Segoe UI', sans-serif;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_stock_data(ticker, period):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period=f"{period}d")
        return stock, info, hist
    except Exception as e:
        return None, None, None

def calculate_signals(df):
    signals = []
    
    # RSI
    current_rsi = df['RSI'].iloc[-1]
    if current_rsi < 30:
        signals.append(("🟢", "Oversold (RSI < 30)", "Potential Buy"))
    elif current_rsi > 70:
        signals.append(("🔴", "Overbought (RSI > 70)", "Potential Sell"))
        
    # MACD
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

# --- SIDEBAR ---
with st.sidebar:
    st.title("📈 ProTrade Analytics")
    
    with st.expander("Asset Selection", expanded=True):
        ticker = st.text_input("Ticker Symbol", "NVDA").upper()
        days_back = st.slider("History (Days)", 365, 2000, 730)
    
    with st.expander("Technical Indicators", expanded=True):
        show_sma = st.checkbox("Show SMA (50/200)", value=True)
        show_rsi = st.checkbox("Show RSI", value=True)
        show_macd = st.checkbox("Show MACD", value=True)
        show_bb = st.checkbox("Show Bollinger Bands", value=False)
        
    with st.expander("Risk Management"):
        account_balance = st.number_input("Account Balance", value=25000, step=1000)
        risk_per_trade = st.slider("Risk per Trade (%)", 0.5, 5.0, 1.0, step=0.1)
# --- MAIN APP ---
if ticker:
    stock, info, hist = get_stock_data(ticker, days_back)
    
    if info and not hist.empty:
        # --- DATA PROCESSING ---
        # Calculate Indicators
        # Explicitly assign to avoid naming issues
        hist['RSI'] = ta.rsi(hist['Close'], length=14)
        
        # MACD returns a DataFrame, so we concat it
        macd = ta.macd(hist['Close'])
        hist = pd.concat([hist, macd], axis=1)
        
        hist['SMA_50'] = ta.sma(hist['Close'], length=50)
        hist['SMA_200'] = ta.sma(hist['Close'], length=200)
        
        # Bollinger Bands
        bbands = ta.bbands(hist['Close'], length=20)
        hist = pd.concat([hist, bbands], axis=1)
        
        # --- HEADER SECTION ---
        col1, col2, col3 = st.columns([2, 4, 2])
        
        with col1:
            st.markdown(f"# {ticker}")
            st.caption(info.get('longName', ''))
            
        with col2:
            current_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            delta = current_price - prev_price
            delta_pct = (delta / prev_price) * 100
            st.metric("Current Price", f"${current_price:.2f}", f"{delta:.2f} ({delta_pct:.2f}%)")
            
        with col3:
            vol = hist['Volume'].iloc[-1]
            avg_vol = hist['Volume'].mean()
            vol_delta = ((vol - avg_vol) / avg_vol) * 100
            st.metric("Volume", f"{vol:,.0f}", f"{vol_delta:.1f}% vs Avg")

        # --- ALERTS & SIGNALS ---
        signals = calculate_signals(hist)
        if signals:
            st.subheader("🔔 Active Signals")
            sig_cols = st.columns(len(signals))
            for i, (icon, title, desc) in enumerate(signals):
                with sig_cols[i]:
                    st.info(f"**{icon} {title}**\n\n{desc}")
        
        # --- TABS ---
        tab_chart, tab_fund, tab_news, tab_calc = st.tabs(["📊 Technical Chart", "🏢 Fundamentals", "📰 News", "🧮 Risk Calculator"])
        
        with tab_chart:
            # Main Chart
            fig = go.Figure()
            
            # Candlesticks
            fig.add_trace(go.Candlestick(x=hist.index,
                open=hist['Open'], high=hist['High'],
                low=hist['Low'], close=hist['Close'],
                name='Price'))
                
            # Overlays
            if show_sma:
                fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_50'], line=dict(color='orange', width=1), name='SMA 50'))
                fig.add_trace(go.Scatter(x=hist.index, y=hist['SMA_200'], line=dict(color='blue', width=1), name='SMA 200'))
            
            if show_bb:
                fig.add_trace(go.Scatter(x=hist.index, y=hist['BBU_20_2.0'], line=dict(color='gray', width=1, dash='dot'), name='Upper BB'))
                fig.add_trace(go.Scatter(x=hist.index, y=hist['BBL_20_2.0'], line=dict(color='gray', width=1, dash='dot'), name='Lower BB'))

            fig.update_layout(height=600, template="plotly_dark", title=f"{ticker} Price Action", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Subplots for Indicators
            if show_rsi:
                fig_rsi = go.Figure(go.Scatter(x=hist.index, y=hist['RSI'], line=dict(color='purple')))
                fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                fig_rsi.update_layout(height=200, template="plotly_dark", title="RSI (14)", margin=dict(t=30))
                st.plotly_chart(fig_rsi, use_container_width=True)
                
            if show_macd:
                fig_macd = go.Figure()
                fig_macd.add_trace(go.Scatter(x=hist.index, y=hist['MACD_12_26_9'], name='MACD'))
                fig_macd.add_trace(go.Scatter(x=hist.index, y=hist['MACDs_12_26_9'], name='Signal'))
                fig_macd.add_trace(go.Bar(x=hist.index, y=hist['MACDh_12_26_9'], name='Hist'))
                fig_macd.update_layout(height=200, template="plotly_dark", title="MACD", margin=dict(t=30))
                st.plotly_chart(fig_macd, use_container_width=True)

        with tab_fund:
            st.subheader("Key Metrics")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Market Cap", f"${info.get('marketCap', 0):,.0f}")
            c2.metric("Trailing P/E", f"{info.get('trailingPE', 0):.2f}")
            c3.metric("Forward P/E", f"{info.get('forwardPE', 0):.2f}")
            c4.metric("EPS (TTM)", f"${info.get('trailingEps', 0):.2f}")
            
            st.divider()
            st.subheader("Business Summary")
            st.write(info.get('longBusinessSummary', 'No summary available.'))
            
        with tab_news:
            
            col_calc1, col_calc2 = st.columns(2)
            
            with col_calc1:
                entry_price = st.number_input("Entry Price", value=float(current_price))
                stop_loss = st.number_input("Stop Loss", value=float(current_price * 0.95))
                take_profit = st.number_input("Take Profit", value=float(current_price * 1.10))
            
            with col_calc2:
                risk_amount = account_balance * (risk_per_trade / 100)
                st.markdown(f"### Risk Amount: **${risk_amount:,.2f}**")
                
                if entry_price > stop_loss:
                    risk_per_share = entry_price - stop_loss
                    reward_per_share = take_profit - entry_price
                    
                    if risk_per_share > 0:
                        shares = int(risk_amount / risk_per_share)
                        position_value = shares * entry_price
                        rr_ratio = reward_per_share / risk_per_share
                        
                        st.success(f"Recommended Position: **{shares} shares**")
                        st.info(f"Total Value: **${position_value:,.2f}**")
                        st.metric("Risk/Reward Ratio", f"1 : {rr_ratio:.2f}")
                    else:
                        st.error("Check your Stop Loss")
                else:
                    st.error("Stop Loss must be below Entry for Long positions.")

    else:
        st.error("Data not available.")
else:
    st.info("Enter a ticker to begin analysis.")