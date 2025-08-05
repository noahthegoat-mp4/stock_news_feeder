<<<<<<< HEAD
import streamlit as st
import requests
import yfinance as yf
from textblob import TextBlob
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

API_KEY = 'f284a65198a04466b2e2354966ef4807'
MAX_DAYS = 30

st.set_page_config(page_title="Stock News Sentiment Tracker", layout="wide")
st.title("\U0001F4F0 Stock News Sentiment Tracker")
st.caption("Enter a company or ticker to view news, sentiment, and stock correlation.")

def get_news(company, start_date, end_date):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': company,
        'from': start_date,
        'to': end_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 20,
        'apiKey': API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get('status') != 'ok':
        st.error(f"Error: {data.get('message')}")
        return [], {}

    articles = data.get('articles', [])
    sentiment_data = []
    sentiment_by_date = {}

    for article in articles:
        title = article.get('title', '')
        desc = article.get('description', '')
        date = article.get('publishedAt', '')[:10]
        source = article['source']['name']
        link = article['url']

        polarity = TextBlob(title).sentiment.polarity
        if polarity > 0:
            sentiment = 'Positive'
        elif polarity < 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        sentiment_by_date.setdefault(date, {'Positive': 0, 'Negative': 0, 'Neutral': 0})
        sentiment_by_date[date][sentiment] += 1

        sentiment_data.append({
            'date': date,
            'title': title,
            'source': source,
            'description': desc,
            'link': link,
            'sentiment': sentiment
        })

    return sentiment_data, sentiment_by_date

def plot_sentiment(sentiment_by_date):
    if not sentiment_by_date:
        return

    dates = sorted(sentiment_by_date.keys())
    positive = [sentiment_by_date[d]['Positive'] for d in dates]
    negative = [sentiment_by_date[d]['Negative'] for d in dates]
    neutral = [sentiment_by_date[d]['Neutral'] for d in dates]

    fig, ax = plt.subplots()
    ax.plot(dates, positive, label='Positive', color='green')
    ax.plot(dates, negative, label='Negative', color='red')
    ax.plot(dates, neutral, label='Neutral', color='gray')
    plt.xticks(rotation=45)
    ax.set_title('Sentiment Over Time')
    ax.set_ylabel('Article Count')
    ax.set_xlabel('Date')
    ax.legend()
    st.pyplot(fig)

@st.cache_data
def get_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

def plot_price_and_sentiment(ticker, sentiment_by_date, start_date, end_date):
    try:
        df = get_stock_data(ticker, start_date, end_date)

        if df.empty:
            st.warning("Could not fetch price data. Check the ticker symbol.")
            return

        df = df.reset_index()
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        df = df.set_index('Date')

        dates = sorted(sentiment_by_date.keys())
        filtered_dates = [d for d in dates if d in df.index]
        if not filtered_dates:
            st.warning("No matching dates between stock data and news.")
            return

        positive = [sentiment_by_date[d]['Positive'] for d in filtered_dates]
        negative = [sentiment_by_date[d]['Negative'] for d in filtered_dates]
        close_prices = [df.loc[d]['Close'] for d in filtered_dates]

        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stock Close Price', color='blue')
        ax1.plot(filtered_dates, close_prices, label='Stock Price', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Sentiment Count')
        ax2.plot(filtered_dates, positive, label='Positive News', color='green', linestyle='dashed')
        ax2.plot(filtered_dates, negative, label='Negative News', color='red', linestyle='dashed')

        fig.autofmt_xdate()
        fig.legend(loc='upper left')
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error fetching or plotting stock data: {e}")

with st.sidebar:
    st.subheader("🔍 Search Settings")
    company_input = st.text_input("Company or Ticker", value="Tesla")
    today = datetime.today().date()
    default_start = today - timedelta(days=7)
    start_date = st.date_input("Start Date", default_start, max_value=today)
    end_date = st.date_input("End Date", today, max_value=today)

    if (today - start_date).days > MAX_DAYS:
        st.warning("Free NewsAPI plan supports only the last 30 days!")

    run_button = st.button("Get News")
    show_stock = st.checkbox("📉 Show stock price correlation", value=True)

if run_button and company_input:
    with st.spinner("Fetching news..."):
        news, sentiment_by_date = get_news(
            company_input,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

    if news:
        st.subheader("🗞️ News Articles")
        for article in news:
            st.markdown(f"**{article['date']}** — [{article['title']}]({article['link']})")
            st.write(f"*{article['sentiment']}* — {article['description']}\n")

        st.subheader("📊 Sentiment Over Time")
        plot_sentiment(sentiment_by_date)

        if show_stock:
            st.subheader("📉 Stock Price vs. News Sentiment")
            plot_price_and_sentiment(
                company_input,
                sentiment_by_date,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
    else:
=======
import streamlit as st
import requests
import yfinance as yf
from textblob import TextBlob
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd

API_KEY = 'f284a65198a04466b2e2354966ef4807'
MAX_DAYS = 30

st.set_page_config(page_title="Stock News Sentiment Tracker", layout="wide")
st.title("\U0001F4F0 Stock News Sentiment Tracker")
st.caption("Enter a company or ticker to view news, sentiment, and stock correlation.")

def get_news(company, start_date, end_date):
    url = 'https://newsapi.org/v2/everything'
    params = {
        'q': company,
        'from': start_date,
        'to': end_date,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': 20,
        'apiKey': API_KEY
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get('status') != 'ok':
        st.error(f"Error: {data.get('message')}")
        return [], {}

    articles = data.get('articles', [])
    sentiment_data = []
    sentiment_by_date = {}

    for article in articles:
        title = article.get('title', '')
        desc = article.get('description', '')
        date = article.get('publishedAt', '')[:10]
        source = article['source']['name']
        link = article['url']

        polarity = TextBlob(title).sentiment.polarity
        if polarity > 0:
            sentiment = 'Positive'
        elif polarity < 0:
            sentiment = 'Negative'
        else:
            sentiment = 'Neutral'

        sentiment_by_date.setdefault(date, {'Positive': 0, 'Negative': 0, 'Neutral': 0})
        sentiment_by_date[date][sentiment] += 1

        sentiment_data.append({
            'date': date,
            'title': title,
            'source': source,
            'description': desc,
            'link': link,
            'sentiment': sentiment
        })

    return sentiment_data, sentiment_by_date

def plot_sentiment(sentiment_by_date):
    if not sentiment_by_date:
        return

    dates = sorted(sentiment_by_date.keys())
    positive = [sentiment_by_date[d]['Positive'] for d in dates]
    negative = [sentiment_by_date[d]['Negative'] for d in dates]
    neutral = [sentiment_by_date[d]['Neutral'] for d in dates]

    fig, ax = plt.subplots()
    ax.plot(dates, positive, label='Positive', color='green')
    ax.plot(dates, negative, label='Negative', color='red')
    ax.plot(dates, neutral, label='Neutral', color='gray')
    plt.xticks(rotation=45)
    ax.set_title('Sentiment Over Time')
    ax.set_ylabel('Article Count')
    ax.set_xlabel('Date')
    ax.legend()
    st.pyplot(fig)

@st.cache_data
def get_stock_data(ticker, start_date, end_date):
    stock = yf.Ticker(ticker)
    return stock.history(start=start_date, end=end_date)

def plot_price_and_sentiment(ticker, sentiment_by_date, start_date, end_date):
    try:
        df = get_stock_data(ticker, start_date, end_date)

        if df.empty:
            st.warning("Could not fetch price data. Check the ticker symbol.")
            return

        df = df.reset_index()
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        df = df.set_index('Date')

        dates = sorted(sentiment_by_date.keys())
        filtered_dates = [d for d in dates if d in df.index]
        if not filtered_dates:
            st.warning("No matching dates between stock data and news.")
            return

        positive = [sentiment_by_date[d]['Positive'] for d in filtered_dates]
        negative = [sentiment_by_date[d]['Negative'] for d in filtered_dates]
        close_prices = [df.loc[d]['Close'] for d in filtered_dates]

        fig, ax1 = plt.subplots(figsize=(10, 5))

        ax1.set_xlabel('Date')
        ax1.set_ylabel('Stock Close Price', color='blue')
        ax1.plot(filtered_dates, close_prices, label='Stock Price', color='blue')
        ax1.tick_params(axis='y', labelcolor='blue')

        ax2 = ax1.twinx()
        ax2.set_ylabel('Sentiment Count')
        ax2.plot(filtered_dates, positive, label='Positive News', color='green', linestyle='dashed')
        ax2.plot(filtered_dates, negative, label='Negative News', color='red', linestyle='dashed')

        fig.autofmt_xdate()
        fig.legend(loc='upper left')
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Error fetching or plotting stock data: {e}")

with st.sidebar:
    st.subheader("🔍 Search Settings")
    company_input = st.text_input("Company or Ticker", value="Tesla")
    today = datetime.today().date()
    default_start = today - timedelta(days=7)
    start_date = st.date_input("Start Date", default_start, max_value=today)
    end_date = st.date_input("End Date", today, max_value=today)

    if (today - start_date).days > MAX_DAYS:
        st.warning("Free NewsAPI plan supports only the last 30 days!")

    run_button = st.button("Get News")
    show_stock = st.checkbox("📉 Show stock price correlation", value=True)

if run_button and company_input:
    with st.spinner("Fetching news..."):
        news, sentiment_by_date = get_news(
            company_input,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )

    if news:
        st.subheader("🗞️ News Articles")
        for article in news:
            st.markdown(f"**{article['date']}** — [{article['title']}]({article['link']})")
            st.write(f"*{article['sentiment']}* — {article['description']}\n")

        st.subheader("📊 Sentiment Over Time")
        plot_sentiment(sentiment_by_date)

        if show_stock:
            st.subheader("📉 Stock Price vs. News Sentiment")
            plot_price_and_sentiment(
                company_input,
                sentiment_by_date,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
    else:
>>>>>>> 0642a5b967926699477b78392c848cbc0efb3fcb
        st.warning("No news found.")