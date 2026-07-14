import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="Global Top10 Market Cap Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("📈 Global Market Cap Top10 Stock Dashboard")
st.caption("최근 1년간 글로벌 시가총액 Top10 기업의 주가 변화")

stocks = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Saudi Aramco": "2222.SR",
    "Broadcom": "AVGO",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK-B"
}

selected = st.multiselect(
    "기업 선택",
    list(stocks.keys()),
    default=list(stocks.keys())
)

@st.cache_data(ttl=3600)
def load_data():

    price = pd.DataFrame()

    for company, ticker in stocks.items():

        df = yf.download(
            ticker,
            period="1y",
            progress=False,
            auto_adjust=True
        )

        if len(df) > 0:
            price[company] = df["Close"]

    return price

prices = load_data()

prices = prices[selected]

# 시작일 기준 100으로 정규화
normalized = prices / prices.iloc[0] * 100

fig = go.Figure()

for col in normalized.columns:
    fig.add_trace(
        go.Scatter(
            x=normalized.index,
            y=normalized[col],
            mode="lines",
            name=col,
            line=dict(width=2)
        )
    )

fig.update_layout(
    title="최근 1년 수익률 비교 (시작일=100)",
    template="plotly_white",
    height=700,
    hovermode="x unified",
    xaxis_title="Date",
    yaxis_title="Normalized Price"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("최근 종가")

latest = pd.DataFrame({
    "Latest Price": prices.iloc[-1].round(2),
    "1Y Return (%)":
        ((prices.iloc[-1]/prices.iloc[0]-1)*100).round(2)
})

st.dataframe(latest.sort_values("1Y Return (%)", ascending=False))

st.subheader("원본 데이터")

st.dataframe(prices.tail())
