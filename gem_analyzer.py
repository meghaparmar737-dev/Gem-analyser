import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Gem Analyzer", layout="wide")

st.title("💎 Intelligent Stock Gem Analyzer")
st.markdown("Type NSE ticker like: TCS.NS, LT.NS, BEL.NS")

ticker = st.text_input("🔍 Enter NSE Stock")

if st.button("Analyze"):

    if ticker == "":
        st.warning("Please enter a stock symbol.")
    else:

        stock = yf.Ticker(ticker)
        data = stock.history(period="1y")

        if data.empty:
            st.error("Invalid stock or no data found.")
        else:

            # ---- Technical ----
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

            # ---- Scoring ----
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
                st.subheader("📊 Technical")
                st.write("Price:", round(current_price,2))
                st.write("50 DMA:", round(dma50,2))
                st.write("200 DMA:", round(dma200,2))
                st.write("RSI:", round(rsi,2))

            with col2:
                st.subheader("📈 Fundamentals")
                st.write("ROE:", roe)
                st.write("Revenue Growth:", revenue_growth)
                st.write("Operating Margin:", operating_margin)
                st.write("Debt/Equity:", debt_to_equity)
                st.write("Free Cash Flow:", free_cashflow)

            st.subheader("🧠 Gem Score")
            st.progress(score / 10)

            if score >= 8:
                st.success("💎 STRONG GEM")
            elif 5 <= score < 8:
                st.warning("🟡 WATCH")
            else:
                st.error("❌ AVOID")

            st.line_chart(data["Close"])
