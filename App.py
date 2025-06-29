import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (
    fetch_stock_data, calculate_technical_indicators, draw_candlestick_chart,
    process_portfolio_file, export_chart, compute_correlation, save_config, load_config
)

st.set_page_config(layout="wide", page_title="📈 Stock Market Visualizer")

st.title("📊 Stock Market Visualizer")

tab1, tab2, tab3 = st.tabs(["📈 Charting", "📂 Portfolio", "⚙️ Configurations"])

with tab1:
    st.subheader("Stock Chart Visualization")

    ticker = st.text_input("Enter Stock Ticker (e.g. RELIANCE)", value="RELIANCE")
    timeframe = st.selectbox("Select Timeframe", ["1mo", "3mo", "6mo", "1y", "5y"])
    overlays = st.multiselect("Select Indicators", ["SMA", "EMA", "RSI", "Bollinger Bands"])

    if st.button("Plot Chart"):
        df = fetch_stock_data(ticker, timeframe)
        if df is not None:
            df = calculate_technical_indicators(df, overlays)
            fig = draw_candlestick_chart(df, overlays, ticker)
            st.plotly_chart(fig, use_container_width=True)

            export_format = st.selectbox("Export Format", ["None", "PNG", "HTML"])
            if export_format != "None":
                export_chart(fig, ticker, export_format)

with tab2:
    st.subheader("Upload Portfolio File")

    file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
    if file:
        portfolio = process_portfolio_file(file)
        st.dataframe(portfolio)

        if st.checkbox("Show Correlation Matrix"):
            corr_fig = compute_correlation(portfolio)
            st.plotly_chart(corr_fig, use_container_width=True)

with tab3:
    st.subheader("Save/Load Your Settings")
    
    config_name = st.text_input("Configuration name", value="sample_config")
    config_file = f"config/{config_name}.json"

    if st.button("💾 Save Config"):
        save_config({
            "ticker": ticker,
            "timeframe": timeframe,
            "indicators": overlays
        }, config_file)
        st.success(f"Configuration saved to {config_file}")

    if st.button("📂 Load Config"):
        config = load_config(config_file)
        if config:
            st.json(config)
        else:
            st.error("Config not found")
