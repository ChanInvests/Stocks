import pandas as pd
import plotly.graph_objects as go
from screener import Screener
import json
import os

def fetch_stock_data(ticker, timeframe):
    try:
        s = Screener()
        df = s.get_historical_data(ticker, timeframe)
        df = pd.DataFrame(df).sort_values('date')
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def calculate_technical_indicators(df, overlays):
    if "SMA" in overlays:
        df["SMA20"] = df["close"].rolling(20).mean()
    if "EMA" in overlays:
        df["EMA20"] = df["close"].ewm(span=20, adjust=False).mean()
    if "RSI" in overlays:
        delta = df["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
    if "Bollinger Bands" in overlays:
        sma = df["close"].rolling(20).mean()
        std = df["close"].rolling(20).std()
        df["BB_upper"] = sma + 2*std
        df["BB_lower"] = sma - 2*std
    return df

def draw_candlestick_chart(df, overlays, ticker):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Candlesticks"
    ))

    if "SMA" in overlays and "SMA20" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], mode='lines', name="SMA 20"))
    if "EMA" in overlays and "EMA20" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA20"], mode='lines', name="EMA 20"))
    if "Bollinger Bands" in overlays:
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_upper"], line=dict(dash='dot'), name='BB Upper'))
        fig.add_trace(go.Scatter(x=df.index, y=df["BB_lower"], line=dict(dash='dot'), name='BB Lower'))

    fig.update_layout(title=f"{ticker} Candlestick Chart", xaxis_rangeslider_visible=False)
    return fig

def export_chart(fig, ticker, format):
    if format == "PNG":
        fig.write_image(f"{ticker}.png")
    elif format == "HTML":
        fig.write_html(f"{ticker}.html")

def process_portfolio_file(file):
    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    elif file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        return None
    return df

def compute_correlation(df):
    df_numeric = df.select_dtypes(include='number')
    corr = df_numeric.corr()
    fig = go.Figure(data=go.Heatmap(z=corr.values, x=corr.columns, y=corr.columns, colorscale='Viridis'))
    fig.update_layout(title="Correlation Matrix")
    return fig

def save_config(config_data, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(config_data, f)

def load_config(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
