import requests
from textblob import TextBlob
import argparse
from datetime import datetime, timedelta
import json
import os
import matplotlib.pyplot as plt

API_KEY = 'f284a65198a04466b2e2354966ef4807'  # Replace with your actual NewsAPI key
CACHE_DIR = 'news_cache'
MIN_DATE = datetime.today() - timedelta(days=30)

def valid_date(date_str):
    """Validate date format and ensure it's within the API's 30-day limit."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if dt < MIN_DATE:
            raise argparse.ArgumentTypeError(f"Date too old: '{date_str}'. Free plan only allows last 30 days.")
        return date_str
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date: '{date_str}'. Use YYYY-MM-DD format.")

def cache_filename(company_name, start_date, end_date):
    parts = [company_name.replace(' ', '_')]
    if start_date:
        parts.append(start_date)
    if end_date:
        parts.append(end_date)
    return os.path.join(CACHE_DIR, "_".join(parts) + '.json')

def save_cache(filename, data):
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f)

def load_cache(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def get_stock_news(company_name, start_date=None, end_date=None):
    filename = cache_filename(company_name, start_date, end_date)
    cached = load_cache(filename)
    if cached:
        print(f"Using cached data for {company_name}")
        data = cached
    else:
        base_url = 'https://newsapi.org/v2/everything?'
        params = {
            'q': company_name,
            'sortBy': 'publishedAt',
            'language': 'en',
            'pageSize': 20,
            'apiKey': API_KEY
        }
        if start_date:
            params['from'] = start_date
        if end_date:
            params['to'] = end_date
        try:
            response = requests.get(base_url, params=params, timeout=10)
            data = response.json()
            if data.get('status') != 'ok':
                print('Error fetching news:', data.get('message'))
                return [], {}, {}
            save_cache(filename, data)
        except requests.exceptions.RequestException as e:
            print("Network error:", e)
            return [], {}, {}

    articles = data.get('articles', [])
    if not articles:
        print(f"No news found for {company_name} in given date range.")
        return [], {}, {}

    news_list = []
    sentiment_counts = {'Positive': 0, 'Negative': 0, 'Neutral': 0}
    sentiment_over_time = {}

    for article in articles:
        title = article.get('title', '')
        description = article.get('description') or ''
        source = article.get('source', {}).get('name', 'Unknown')
        published = article.get('publishedAt', '')[:10]
        url = article.get('url', '')

        polarity = TextBlob(title).sentiment.polarity
        if polarity > 0:
            sentiment = 'Positive'
            sentiment_counts['Positive'] += 1
        elif polarity < 0:
            sentiment = 'Negative'
            sentiment_counts['Negative'] += 1
        else:
            sentiment = 'Neutral'
            sentiment_counts['Neutral'] += 1

        sentiment_over_time.setdefault(published, {'Positive':0, 'Negative':0, 'Neutral':0})
        sentiment_over_time[published][sentiment] += 1

        news_item = (
            f"{published} - {title} ({source})\n"
            f"Sentiment: {sentiment}\n"
            f"{description}\n"
            f"Read more: {url}\n"
        )
        news_list.append(news_item)

    return news_list, sentiment_counts, sentiment_over_time

def plot_sentiment_over_time(sentiment_over_time, company_name):
    if not sentiment_over_time:
        print("No sentiment data to plot.")
        return

    dates = sorted(sentiment_over_time.keys())
    positive = [sentiment_over_time[date]['Positive'] for date in dates]
    negative = [sentiment_over_time[date]['Negative'] for date in dates]
    neutral = [sentiment_over_time[date]['Neutral'] for date in dates]

    plt.figure(figsize=(10,5))
    plt.plot(dates, positive, label='Positive', color='green', marker='o')
    plt.plot(dates, negative, label='Negative', color='red', marker='o')
    plt.plot(dates, neutral, label='Neutral', color='gray', marker='o')
    plt.xlabel('Date')
    plt.ylabel('Number of Articles')
    plt.title(f'Sentiment Over Time for {company_name}')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    parser = argparse.ArgumentParser(description="Stock News Feeder with Sentiment, Caching, and Plotting")
    parser.add_argument('company', nargs='?', help='Company name or ticker (e.g., Apple or AAPL)')
    parser.add_argument('--start', type=valid_date, help='Start date YYYY-MM-DD (within last 30 days)')
    parser.add_argument('--end', type=valid_date, help='End date YYYY-MM-DD')
    args = parser.parse_args()

    company = args.company
    if not company:
        company = input("Enter company name or stock ticker (e.g., Apple or AAPL): ").strip()

    news, sentiment_counts, sentiment_over_time = get_stock_news(company, start_date=args.start, end_date=args.end)

    if news:
        print(f"\nLatest news about {company}:\n")
        for item in news:
            print(item)

        print("Sentiment summary:")
        for sentiment, count in sentiment_counts.items():
            print(f"  {sentiment}: {count}")

        plot_sentiment_over_time(sentiment_over_time, company)
    else:
        print("No news to display.")

if __name__ == '__main__':
    main()
