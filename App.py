import streamlit as st
from utils.data_utils import load_data
from utils.chart_utils import plot_candlestick
from utils.indicators import add_indicators
from utils.portfolio_utils import load_portfolio, show_correlation
import json
import io

st.set_page_config(page_title="Stock Market Visualizer", layout="wide")
st.title("📈 Stock Market Visualizer")

with st.sidebar:
    st.header("Settings")
    ticker = st.text_input("Stock Ticker", value="AAPL")
    period = st.selectbox("Data Period", options=["1mo", "3mo", "6mo", "1y", "5y", "max"], index=3)
    interval = st.selectbox("Interval", options=["1d", "1wk", "1mo"], index=0)

    st.subheader("Indicators")
    sma_period = st.slider("SMA Period", 5, 100, 20)
    show_rsi = st.checkbox("Show RSI", value=True)
    show_bbands = st.checkbox("Show Bollinger Bands", value=True)

    st.subheader("Export")
    export_format = st.selectbox("Export Format", ["PNG", "HTML"])
    if st.button("Save Config"):
        config = {
            "ticker": ticker, "period": period, "interval": interval,
            "sma_period": sma_period, "show_rsi": show_rsi, "show_bbands": show_bbands
        }
        st.download_button("Download Config", json.dumps(config), file_name="config.json")

data = load_data(ticker, period, interval)
if data.empty:
    st.error("No data found. Check ticker or timeframe.")
else:
    st.subheader(f"{ticker} Candlestick Chart")
    fig = plot_candlestick(data, sma_period, show_bbands)
    st.plotly_chart(fig, use_container_width=True)

    if show_rsi:
        st.subheader("Relative Strength Index (RSI)")
        rsi_fig = add_indicators(data, indicator='rsi')
        st.plotly_chart(rsi_fig, use_container_width=True)

    if export_format == "PNG":
        st.download_button("Download PNG", fig.to_image(format="png"), file_name=f"{ticker}.png")
    else:
        html_bytes = fig.to_html().encode("utf-8")
        st.download_button("Download HTML", html_bytes, file_name=f"{ticker}.html")

    st.divider()

    st.subheader("📊 Portfolio Upload")
    uploaded_file = st.file_uploader("Upload CSV or Excel (tickers in first column)", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            tickers = load_portfolio(uploaded_file)
            show_correlation(tickers, period)
        except Exception as e:
            st.error(f"Error processing portfolio: {e}")
