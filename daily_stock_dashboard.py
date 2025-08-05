import streamlit as st
import requests
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import pandas as pd
from textblob import TextBlob

# ---------- CONFIG ----------
FINNHUB_API_KEY = "d28q47hr01qmp5ua07i0d28q47hr01qmp5ua07ig"  # Replace with your Finnhub API key
DEFAULT_DAYS_HISTORY = 14

# Popular liquid stocks for reliable data
POPULAR_TICKERS = [
    "AAPL", "MSFT", "TSLA", "AMZN", "GOOGL", "META", "NVDA", "NFLX", "AMD", "INTC"
]

# ---------- FUNCTIONS ----------

@st.cache_data(ttl=3600)
def get_top_gainers_from_list(tickers):
    gainers = []
    for sym in tickers:
        try:
            stock = yf.Ticker(sym)
            hist = stock.history(period="5d")  # Increased lookback period
            if hist.empty or len(hist) < 2:
                continue
            
            hist_sorted = hist.sort_index(ascending=False)
            latest_close = hist_sorted['Close'].iloc[0]
            prev_close = hist_sorted['Close'].iloc[1]

            change_pct = (latest_close - prev_close) / prev_close * 100
            gainers.append({'symbol': sym, 'change_pct': change_pct})
        except Exception:
            continue
    gainers.sort(key=lambda x: x['change_pct'], reverse=True)
    return gainers

@st.cache_data(ttl=1800)
def get_stock_news(symbol, from_date, to_date):
    url = f'https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}'
    resp = requests.get(url)
    if resp.status_code != 200:
        return []
    return resp.json()

def analyze_sentiment(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.1:
        return "Positive", "😊"
    elif polarity < -0.1:
        return "Negative", "😠"
    else:
        return "Neutral", "😐"

@st.cache_data(ttl=3600)
def get_price_history(symbol, start_date, end_date):
    stock = yf.Ticker(symbol)
    df = stock.history(start=start_date, end=end_date)
    return df

def plot_price_chart(symbol, df):
    if df.empty:
        st.warning(f"No price data for {symbol}")
        return
    plt.figure(figsize=(8, 3))
    plt.plot(df.index, df['Close'], marker='o')
    plt.title(f"{symbol} Closing Prices")
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()

def plot_correlation(selected_symbols, start_date, end_date):
    price_data = {}
    for sym in selected_symbols:
        df = get_price_history(sym, start_date, end_date)
        if df.empty:
            continue
        price_data[sym] = df['Close']

    if len(price_data) < 2:
        st.warning("Need at least two stocks with data for correlation.")
        return

    prices_df = pd.DataFrame(price_data)
    returns = prices_df.pct_change().dropna()

    corr = returns.corr()

    st.subheader("📈 Price Correlation Matrix")
    st.dataframe(corr.style.background_gradient(cmap='coolwarm').format("{:.2f}"))

    st.subheader("📊 Price Comparison Chart")
    plt.figure(figsize=(10, 5))
    for sym in prices_df.columns:
        plt.plot(prices_df.index, prices_df[sym], label=sym)
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Price ($)")
    plt.title("Stock Prices Comparison")
    plt.grid(True)
    st.pyplot(plt)
    plt.clf()

# ---------- STREAMLIT APP ----------

st.title("🔥 Daily Hot Stocks Dashboard with Sentiment & Correlation")

days_option = st.sidebar.selectbox("Select Time Frame (days)", [7, 14, 30], index=1)
end_date = datetime.now().date()
start_date = end_date - timedelta(days=days_option)

st.sidebar.write(f"Using a fixed list of popular stocks: {', '.join(POPULAR_TICKERS)}")

with st.spinner("Calculating top gainers..."):
    gainers = get_top_gainers_from_list(POPULAR_TICKERS)

st.sidebar.write(f"Top gainers found: {len(gainers)}")

if not gainers:
    st.error("No gainers found! Try again later.")
    st.stop()

for stock in gainers:
    sym = stock['symbol']
    change = stock['change_pct']
    st.header(f"{sym}  ({change:.2f}% ↑)")

    news_items = get_stock_news(sym, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    if news_items:
        st.subheader("Top News with Sentiment")
        for news in news_items[:5]:
            headline = news.get('headline', 'No title')
            sentiment, emoji = analyze_sentiment(headline)
            dt = datetime.fromtimestamp(news['datetime']).strftime('%Y-%m-%d %H:%M')
            url = news.get('url', '#')
            st.markdown(f"- [{headline}]({url}) — *{sentiment}* {emoji} — {dt}")
    else:
        st.write("No recent news.")

    price_df = get_price_history(sym, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    st.subheader("Price Chart")
    plot_price_chart(sym, price_df)

    st.markdown("---")

selected_stocks = st.sidebar.multiselect(
    "Select stocks to compare (from gainers):",
    [s['symbol'] for s in gainers]
)

if selected_stocks:
    plot_correlation(selected_stocks, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
