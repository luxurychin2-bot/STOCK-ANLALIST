import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Sector Rotation", layout="wide")
st.title("📊 Sector Rotation Dashboard")

SECTOR_ETF = {
    "AI": "BOTZ",
    "BIO": "IBB",
    "SEMICON": "SOXX",
    "ENERGY": "XLE",
    "DEFENSE": "ITA"
}

START = "2018-01-01"

def load_price(ticker):
    df = yf.download(ticker, start=START, progress=False)
    return df[['Close']].dropna()

def calculate_score(df):
    df['ma20'] = df['Close'].rolling(20).mean()
    df['ma60'] = df['Close'].rolling(60).mean()
    return 20 if df['ma20'].iloc[-1] > df['ma60'].iloc[-1] else 0

scores = {}
for name, ticker in SECTOR_ETF.items():
    df = load_price(ticker)
    if len(df) > 60:
        scores[name] = calculate_score(df)

top2 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]

st.subheader("🔥 이번 달 상위 2개 섹터")
for name, score in top2:
    st.write(f"• {name} | 점수: {score}")
