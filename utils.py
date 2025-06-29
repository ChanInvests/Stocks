# utils.py

import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

# ------------------ Data Loading ------------------ #

def load_data(ticker, period="1y", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval)
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# ------------------ Indicators ------------------ #

def calculate_sma(series, window):
    return series.rolling(window=window).mean()

def calculate_bollinger(series, window=20):
    sma = series.rolling(window).mean()
    std = series.rolling(window).std()
    upper = sma + (2 * std)
    lower = sma - (2 * std)
    return upper, lower

def add_rsi_plot(df, period=14):
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi

    fig = px.line(df, x='Date', y='RSI', title='RSI (14)')
    fig.add_hline(y=70, line_dash="dot", line_color="red")
    fig.add_hline(y=30, line_dash="dot", line_color="green")
    return fig

# ------------------ Charting ------------------ #

def plot_candlestick(df, sma_period=20, show_bbands=True):
    fig = go.Figure(data=[go.Candlestick(x=df['Date'],
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=df['Close'],
                                         name="Candlestick")])

    df['SMA'] = calculate_sma(df['Close'], sma_period)
    fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA'], line=dict(color='blue'), name='SMA'))

    if show_bbands:
        upper, lower = calculate_bollinger(df['Close'])
        fig.add_trace(go.Scatter(x=df['Date'], y=upper, line=dict(color='green'), name='Upper BB'))
        fig.add_trace(go.Scatter(x=df['Date'], y=lower, line=dict(color='red'), name='Lower BB'))

    fig.update_layout(xaxis_rangeslider_visible=False,
                      title=f"Candlestick with SMA and Bollinger Bands",
                      margin=dict(t=40, b=20))
    return fig

# ------------------ Portfolio Utilities ------------------ #

def load_portfolio(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)
    return df.iloc[:, 0].dropna().tolist()

def show_correlation(tickers, period="6mo"):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, period=period)['Close']
            data[ticker] = df
        except:
            continue

    if len(data) < 2:
        st.warning("Need at least two valid tickers for correlation.")
        return

    df_corr = pd.DataFrame(data).pct_change().corr()
    st.write("### 📉 Stock Correlation Heatmap")
    st.dataframe(df_corr.round(2))

    sns.heatmap(df_corr, annot=True, cmap="coolwarm", fmt=".2f")
    st.pyplot(plt.gcf())
    plt.clf()
