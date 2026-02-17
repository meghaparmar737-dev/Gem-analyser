import streamlit as st
import yfinance as yf
import pandas as pd
import requests
import numpy as np

st.set_page_config(page_title="Gem Analyzer", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.stApp {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
}
</style>
""", unsafe_allow_html=True)

st.title("💎 Intelligent Stock Gem Analyzer")

# ---------- YAHOO SEARCH API ----------
def search_yahoo(query):
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}"
    response = requests.get(url).json()
    results = []
    for item in response.get("quotes", []):
        if item.get("symbol", "").endswith(".NS"):
            results.append(item["symbol"])
    return results[:10]

query = st.text_input("🔍 Search NSE Stock")

selected_ticker = None

if query:
    suggestions = search_yahoo(query)
    if suggestions:
        selected_ticker = st.selectbox("Select Stock", suggestions)

if selected_ticker and st.button("Analyze Stock"):

    stock = yf.Ticker(selected_ticker)
    data = stock.history(period="1y")

    if data.empty:
        st.error("Invalid stock data.")
    else:

        # Technical Indicators
        data["50DMA"] = data["Close"].rolling(50).mean()
        data["200DMA"] = data["Close"].rolling(200).mean()

        delta = data["Close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        current_price = data["Close"].iloc[-1]
        dma50 = data["50DMA"].iloc[-1]
        dma200 = data["200DMA"].iloc[-1]
        rsi = data["RSI"].iloc[-1]

        info = stock.info
        roe = info.get("returnOnEquity", 0)
        revenue_growth = info.get("revenueGrowth", 0)
        operating_margin = info.get("operatingMargins", 0)
        debt_to_equity = info.get("debtToEquity", 0)
        free_cashflow = info.get("freeCashflow", 0)

        # Scoring
        score = 0
        if current_price > dma200: score += 2
        if current_price > dma50: score += 1
        if 45 < rsi < 65: score += 1
        if roe and roe > 0.18: score += 2
        if revenue_growth and revenue_growth > 0.12: score += 1
        if operating_margin and operating_margin > 0.15: score += 1
        if debt_to_equity and debt_to_equity < 100: score += 1
        if free_cashflow and free_cashflow > 0: score += 1

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📊 Technical")
            st.write("Price:", round(current_price,2))
            st.write("50 DMA:", round(dma50,2))
            st.write("200 DMA:", round(dma200,2))
            st.write("RSI:", round(rsi,2))
            st.markdown("</div>", unsafe_allow_html=True)

        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.subheader("📈 Fundamentals")
            st.write("ROE:", roe)
            st.write("Revenue Growth:", revenue_growth)
            st.write("Operating Margin:", operating_margin)
            st.write("Debt/Equity:", debt_to_equity)
            st.write("Free Cash Flow:", free_cashflow)
            st.markdown("</div>", unsafe_allow_html=True)

        st.subheader("🧠 Gem Score")
        st.progress(score / 10)

        if score >= 8:
            st.success("💎 STRONG GEM")
        elif 5 <= score < 8:
            st.warning("🟡 WATCH")
        else:
            st.error("❌ AVOID")

        st.line_chart(data["Close"])
