import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# =====================
# 기본 설정
# =====================
st.set_page_config(page_title="Sector Rotation Dashboard", layout="wide")
st.title("📊 Sector Rotation Dashboard")

# =====================
# 섹터 정의 (추후 한국 ETF로 교체 가능)
# =====================
SECTOR_ETF = {
    "AI": "BOTZ",
    "BIO": "IBB",
    "SEMICON": "SOXX",
    "ENERGY": "XLE",
    "DEFENSE": "ITA"
}

START = "2018-01-01"

# =====================
# 데이터 로딩
# =====================
@st.cache_data
def load_price(ticker):
    df = yf.download(ticker, start=START, progress=False)
    if df.empty:
        return None
    df = df[["Close"]].dropna()
    return df

# =====================
# 점수 계산 (안전 버전)
# =====================
def calculate_score(df):
    if df is None or len(df) < 130:
        return 0

    df = df.copy()
    df["ma20"] = df["Close"].rolling(20).mean()
    df["ma60"] = df["Close"].rolling(60).mean()
    df["ma120"] = df["Close"].rolling(120).mean()

    last = df.iloc[-1]

    score = 0
    if last["Close"] > last["ma20"]:
        score += 1
    if last["ma20"] > last["ma60"]:
        score += 1
    if last["ma60"] > last["ma120"]:
        score += 1

    return score

# =====================
# 섹터 점수 계산
# =====================
scores = {}
price_data = {}

for sector, ticker in SECTOR_ETF.items():
    df = load_price(ticker)
    price_data[sector] = df
    scores[sector] = calculate_score(df)

score_df = pd.DataFrame.from_dict(scores, orient="index", columns=["Score"])
score_df = score_df.sort_values("Score", ascending=False)

# =====================
# 상위 섹터 표시
# =====================
st.subheader("🔥 이번 달 상위 섹터")
for sector, row in score_df.head(2).iterrows():
    st.write(f"• **{sector}** | 점수: {row['Score']}")

# =====================
# 섹터 점수 차트
# =====================
st.subheader("📊 섹터별 모멘텀 점수")

fig, ax = plt.subplots()
score_df["Score"].astype(int).plot(kind="bar", ax=ax)
ax.set_ylabel("Score")
ax.set_xlabel("Sector")
ax.set_ylim(0, 3)

st.pyplot(fig)

# =====================
# 선택 섹터 차트
# =====================
st.subheader("📈 섹터 가격 추이")

selected = st.selectbox("섹터 선택", list(SECTOR_ETF.keys()))

df = price_data[selected]
if df is not None:
    fig2, ax2 = plt.subplots()
    ax2.plot(df.index, df["Close"], label="Close")
    ax2.set_title(f"{selected} Price")
    ax2.legend()
    st.pyplot(fig2)
else:
    st.warning("데이터가 없습니다.")
