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

def calculate_score(df):
    score = 0

    df = df.copy()
    df["ma120"] = df["Close"].rolling(120).mean()

    # 🔒 데이터 길이 안전장치
    if len(df) < 130:
        return 0

    close = float(df["Close"].iloc[-1])
    ma120 = float(df["ma120"].iloc[-1])

    if pd.isna(ma120):
        return 0

    if close > ma120:
        score += 10

    # 20일 모멘텀
    momentum = (close / float(df["Close"].iloc[-21]) - 1) * 100
    if momentum > 0:
        score += 10

    return score
    
def calculate_score(df):
    df['ma20'] = df['Close'].rolling(20).mean()
    df['ma60'] = df['Close'].rolling(60).mean()
    return 20 if df['ma20'].iloc[-1] > df['ma60'].iloc[-1] else 0

scores = {}

for name, ticker in SECTOR_ETF.items():
    df = load_price(ticker)

    if len(df) < 120:
        continue

    score = calculate_score(df)
    scores[name] = score

top2 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]

top2 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:2]

st.subheader("🔥 이번 달 상위 2개 섹터")
for name, score in top2:
    st.write(f"• {name} | 점수: {score}")

SECTOR_ETF = {
    "반도체": "091160",     # KODEX 반도체
    "2차전지": "305720",   # KODEX 2차전지
    "바이오": "244580",     # KODEX 바이오
    "자동차": "091180",    # KODEX 자동차
    "인터넷": "266360",    # KODEX IT
}

def calculate_score(df):
    df["ret20"] = df["Close"].pct_change(20)
    df["ret60"] = df["Close"].pct_change(60)
    df["ma120"] = df["Close"].rolling(120).mean()

    score = 0
    if df["ret20"].iloc[-1] > 0:
        score += 10
        
    if df["ret60"].iloc[-1] > 0:
        score += 10
        
    df["ma120"] = df["Close"].rolling(120).mean()

    if pd.isna(df["ma120"].iloc[-1]):
    return 0

    return score

def plot_sector_chart(df, name):
    st.subheader(f"📈 {name} 차트")
    st.line_chart(df[["Close"]])

scores = {}

for name, code in SECTOR_ETF.items():
    ticker = f"{code}.KS"
    df = yf.download(ticker, start="2018-01-01", progress=False)

    if len(df) < 150:
        continue

    score = calculate_score(df)
    scores[name] = score

    plot_sector_chart(df, name)
    st.write(f"🔥 점수: {score}")

st.header("🔥 섹터 점수 랭킹")

ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

for name, score in ranked:
    st.write(f"• {name} : {score}점")

def monthly_backtest():
    monthly_returns = []

    dates = pd.date_range("2019-01-01", pd.Timestamp.today(), freq="M")

    for date in dates:
        best_sector = None
        best_score = -1

        for name, code in SECTOR_ETF.items():
            ticker = f"{code}.KS"
            df = yf.download(ticker, start="2018-01-01", end=date, progress=False)

            if len(df) < 150:
                continue

            score = calculate_score(df)
            if score > best_score:
                best_score = score
                best_sector = df

        if best_sector is not None:
            ret = best_sector["Close"].pct_change().iloc[-1]
            monthly_returns.append(ret)

    equity = (1 + pd.Series(monthly_returns)).cumprod()
    return equity
