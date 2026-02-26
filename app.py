import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# ===============================
# 기본 설정
# ===============================
st.set_page_config(page_title="Sector Rotation Dashboard", layout="wide")
st.title("📊 Sector Rotation Dashboard")

START_DATE = "2018-01-01"

# 미국 ETF (안정판)
SECTOR_ETF = {
    "AI": "BOTZ",
    "BIO": "IBB",
    "SEMICON": "SOXX",
    "ENERGY": "XLE",
    "DEFENSE": "ITA"
}

# ===============================
# 데이터 로드 함수
# ===============================
@st.cache_data
def load_price(ticker):
    df = yf.download(ticker, start=START_DATE, progress=False)
    df = df[['Close']].dropna()
    return df

# ===============================
# 점수 계산 함수 (추세 기반)
# ===============================
def calculate_score(df):
    df = df.copy()
    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma60"] = df["Close"].rolling(60).mean()
    df["ma120"] = df["Close"].rolling(120).mean()

    if len(df) < 120:
        return 0

    score = 0
    last = df.iloc[-1]

    if last["Close"] > last["ma20"]:
        score += 5
    if last["ma20"] > last["ma60"]:
        score += 5
    if last["ma60"] > last["ma120"]:
        score += 5
    if last["Close"] > last["ma120"]:
        score += 5

    return score

# ===============================
# 섹터 점수 계산
# ===============================
scores = {}
prices = {}

for sector, ticker in SECTOR_ETF.items():
    df = load_price(ticker)
    prices[sector] = df
    scores[sector] = calculate_score(df)

score_df = pd.DataFrame.from_dict(scores, orient="index", columns=["Score"])
score_df = score_df.sort_values("Score", ascending=False)

# ===============================
# 상위 섹터 표시
# ===============================
st.subheader("🔥 이번 달 상위 2개 섹터")
top2 = score_df.head(2)

for sector, row in top2.iterrows():
    st.write(f"• **{sector}** | 점수: {int(row['Score'])}")

# ===============================
# 섹터별 차트
# ===============================
st.subheader("📈 섹터별 가격 차트")

fig, ax = plt.subplots(figsize=(12, 5))

for sector, df in prices.items():
    ax.plot(df.index, df["Close"], label=sector)

ax.set_title("Sector Price Comparison")
ax.legend()
st.pyplot(fig)

# ===============================
# 백테스트 (월별 리밸런싱, Top1)
# ===============================
st.subheader("📊 전략 백테스트 (월 단위, Top1 섹터)")

monthly_returns = []

for date in pd.date_range("2019-01-01", pd.Timestamp.today(), freq="M"):
    month_scores = {}

    for sector, ticker in SECTOR_ETF.items():
        df = load_price(ticker)
        df = df[df.index <= date]

        if len(df) < 120:
            continue

        month_scores[sector] = calculate_score(df)

    if not month_scores:
        monthly_returns.append(0)
        continue

    best_sector = max(month_scores, key=month_scores.get)
    best_df = prices[best_sector]

    try:
        ret = best_df["Close"].pct_change().loc[date]
        monthly_returns.append(0 if pd.isna(ret) else ret)
    except:
        monthly_returns.append(0)

bt = pd.Series(monthly_returns).fillna(0)
equity = (1 + bt).cumprod()

fig2, ax2 = plt.subplots(figsize=(12, 4))
ax2.plot(equity.values)
ax2.set_title("Backtest Equity Curve")
st.pyplot(fig2)
