import streamlit as st
import yfinance as yf
import pandas_ta as ta
from prophet import Prophet
from prophet.plot import plot_plotly
import pandas as pd

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Chill Algo Trader")

st.title("🐢 Chill Investor Dashboard")
st.markdown("*> Low Risk • Fundamentals First • Long Term*")

# --- SIDEBAR INPUTS ---
st.sidebar.header("1. Pick a Stock")
ticker = st.sidebar.text_input("Ticker Symbol", "MSFT").upper()

st.sidebar.header("2. Safety Filters (Fundamentals)")
max_pe = st.sidebar.number_input("Max P/E Ratio", value=30.0, step=1.0)
max_debt = st.sidebar.number_input("Max Debt-to-Equity", value=2.0, step=0.1)
min_beta = st.sidebar.slider("Max Volatility (Beta)", 0.5, 2.0, 1.2)

st.sidebar.header("3. Analysis Settings")
days_back = st.sidebar.slider("History (Days)", 365, 2000, 730)

# --- MAIN LOGIC ---
if st.button("Analyze Stock"):
    with st.spinner(f"Analyzing {ticker}..."):
        try:
            # 1. Get Fundamental Data
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Safe extraction (some stocks miss data)
            pe_ratio = info.get('trailingPE', 0)
            debt_equity = info.get('debtToEquity', 0) / 100  # yfinance returns %
            beta = info.get('beta', 1)
            name = info.get('longName', ticker)
            summary = info.get('longBusinessSummary', 'No summary available.')
            
            # 2. Display Fundamentals First
            st.subheader(f"Step 1: Fundamental Health Check - {name}")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # P/E Logic
            is_pe_good = 0 < pe_ratio <= max_pe
            col1.metric("P/E Ratio", f"{pe_ratio:.2f}", delta="✅ Good" if is_pe_good else "❌ Expensive/Loss", delta_color="normal")
            
            # Debt Logic
            is_debt_good = debt_equity <= max_debt
            col2.metric("Debt/Equity", f"{debt_equity:.2f}", delta="✅ Safe" if is_debt_good else "❌ High Debt", delta_color="normal" if is_debt_good else "inverse")
            
            # Beta Logic
            is_beta_good = beta <= min_beta
            col3.metric("Beta (Volatility)", f"{beta:.2f}", delta="✅ Stable" if is_beta_good else "⚠️ Volatile", delta_color="inverse")
            
            # Dividend
            div_yield = info.get('dividendYield', 0)
            div_display = f"{div_yield*100:.2f}%" if div_yield else "0%"
            col4.metric("Dividend Yield", div_display)

            # Final Verdict on Fundamentals
            if is_pe_good and is_debt_good and is_beta_good:
                st.success(f"💎 **FUNDAMENTAL VERDICT:** {ticker} is a solid, low-risk candidate!")
            else:
                st.warning(f"⚠️ **CAUTION:** {ticker} failed some safety checks. Be careful.")
            
            with st.expander("See Company Description"):
                st.write(summary)

            st.divider()

            # 3. Technical Analysis (The "When")
            st.subheader("Step 2: Price Trend & Prediction")
            
            # Get Price Data
            data = yf.download(ticker, period=f"{days_back}d")
            
            if len(data) > 0:
                # Calculate Indicators
                data['EMA_50'] = ta.ema(data['Close'], length=50)
                data['EMA_200'] = ta.ema(data['Close'], length=200)
                
                # Prepare for Prophet
                df_prophet = data.reset_index()[['Date', 'Close']]
                df_prophet.columns = ['ds', 'y']
                # Convert timezone-aware datetimes to timezone-naive
                df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)

                
                # Forecast
                m = Prophet()
                m.fit(df_prophet)
                future = m.make_future_dataframe(periods=90) # 3 Month forecast
                forecast = m.predict(future)
                
                # Charts
                tab1, tab2 = st.tabs(["🔮 Future Prediction", "📊 EMA Trends"])
                
                with tab1:
                    st.write("### 90-Day Forecast Range")
                    fig1 = plot_plotly(m, forecast)
                    st.plotly_chart(fig1, use_container_width=True)
                    
                with tab2:
                    st.write("### EMA 50 vs EMA 200")
                    st.line_chart(data[['Close', 'EMA_50', 'EMA_200']])
                    
            else:
                st.error("No price data found.")

        except Exception as e:
            st.error(f"An error occurred: {e}")