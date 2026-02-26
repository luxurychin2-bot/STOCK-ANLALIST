import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------
# 기본 설정
# ------------------------
st.set_page_config(page_title="Sector Rotation Dashboard", layout="wide")
st.title("📊 Sector Rotation Dashboard")

START_DATE = "2018-01-01"

SECTOR_ETF = {
    "AI": "BOTZ",
    "BIO": "IBB",
    "SEMICON": "SOXX",
    "ENERGY": "XLE",
    "DEFENSE": "ITA",
}

# ------------------------
# 데이터 로드
# ------------------------
@st.cache_data
def load_price(ticker):
    df = yf.download(ticker, start=START_DATE, progress=False)
    df = df[["Close"]].dropna()
    return df

# ------------------------
# 점수 계산 (안정 버전)
# ------------------------
def calculate_score(df):
    df = df.copy()

    if len(df) < 130:
        return 0

    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma60"] = df["Close"].rolling(60).mean()
    df["ma120"] = df["Close"].rolling(120).mean()

    last = df.iloc[-1]

    close = float(last["Close"])
    ma20 = float(last["ma20"])
    ma60 = float(last["ma60"])
    ma120 = float(last["ma120"])

    score = 0
    if close > ma20:
        score += 1
    if close > ma60:
        score += 1
    if close > ma120:
        score += 1
    if ma20 > ma60:
        score += 1
    if ma60 > ma120:
        score += 1


# ------------------------
# 섹터 점수 계산
# ------------------------
scores = {}
price_data = {}

for sector, ticker in SECTOR_ETF.items():
    df = load_price(ticker)
    price_data[sector] = df
    scores[sector] = calculate_score(df)

# ------------------------
# 상위 섹터 표시
# ------------------------
st.subheader("🔥 현재 상위 섹터")

score_df = (
    pd.DataFrame.from_dict(scores, orient="index", columns=["Score"])
    .sort_values("Score", ascending=False)
)

st.dataframe(score_df)

# ------------------------
# 섹터 점수 차트
# ------------------------
st.subheader("📈 섹터 점수 비교")

fig, ax = plt.subplots()
score_df["Score"].plot(kind="bar", ax=ax)
ax.set_ylabel("Score")
ax.set_xlabel("Sector")
st.pyplot(fig)

# ------------------------
# 월별 누적 수익률 비교
# ------------------------
st.subheader("📊 월별 섹터 성과 비교")

monthly_returns = {}

for sector, df in price_data.items():
    m = df["Close"].resample("M").last().pct_change()
    monthly_returns[sector] = (1 + m).cumprod()

monthly_df = pd.DataFrame(monthly_returns)

fig2, ax2 = plt.subplots()
monthly_df.plot(ax=ax2)
ax2.set_title("Cumulative Return by Sector")
ax2.set_ylabel("Growth")
st.pyplot(fig2)
