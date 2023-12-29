# Ahthesham Ali Syed.
# 12-09-2023.
# Sentiment Analyzer for Stock News.
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import concurrent.futures

# Constants
FINVIZ_URL = 'https://finviz.com/quote.ashx?t='
TICKERS = ['AMZN', 'AMD', 'NVDA', 'META']
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'


# Function to fetch HTML content
def fetch_html(ticker):
    try:
        url = f"{FINVIZ_URL}{ticker}"
        req = Request(url=url, headers={'user-agent': USER_AGENT})
        with urlopen(req) as response:
            html = BeautifulSoup(response, features='html.parser')
        return html
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None


# Function to parse HTML content
def parse_html(html, ticker):
    news_table = html.find(id='news-table')
    parsed_data = []
    current_date = datetime.now().date()

    if news_table:
        for row in news_table.findAll('tr'):
            a_tag = row.a
            if a_tag:
                title = a_tag.text.strip()
                date_data = row.td.text.strip().split(' ')

                if len(date_data) == 1:
                    time = date_data[0]
                else:
                    date = date_data[0]
                    time = date_data[1]

                if date == 'Today':
                    date = current_date

                parsed_data.append([ticker, date, time, title])

    return parsed_data


# Function to perform sentiment analysis
def sentiment_analysis(df):
    vader = SentimentIntensityAnalyzer()
    f = lambda title: vader.polarity_scores(title)['compound']
    df['compound'] = df['title'].apply(f)
    return df


# Fetch and parse data concurrently
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {executor.submit(fetch_html, ticker): ticker for ticker in TICKERS}
    all_parsed_data = []

    for future in concurrent.futures.as_completed(futures):
        ticker = futures[future]
        html = future.result()
        if html:
            parsed_data = parse_html(html, ticker)
            all_parsed_data.extend(parsed_data)

# Create DataFrame
df = pd.DataFrame(all_parsed_data, columns=['ticker', 'date', 'time', 'title'])

# Convert 'date' to datetime and handle missing values
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df.dropna(subset=['date'], inplace=True)
df['date'] = df['date'].dt.date

# Perform Sentiment Analysis
df = sentiment_analysis(df)

# Convert 'date' to the correct format if necessary and ensure it's a datetime type
df['date'] = pd.to_datetime(df['date'], errors='coerce').dt.strftime('%Y-%m-%d')

# Only keep rows where 'date' could be converted successfully
df = df.dropna(subset=['date'])

# Group by 'ticker' and 'date' and then calculate the mean sentiment
grouped_df = df.groupby(['ticker', 'date'])['compound'].mean().reset_index()

# Pivot the DataFrame to have dates on the x-axis and tickers as separate columns
pivot_df = grouped_df.pivot(index='date', columns='ticker', values='compound')

# Plotting with Check for Empty DataFrame
if not pivot_df.empty:
    pivot_df.plot(kind='bar', figsize=(14, 8), width=0.8)
    plt.title("Sentiment Analysis of Stock News")
    plt.xlabel("Date")
    plt.ylabel("Average Sentiment")
    plt.legend(title='Ticker')
    plt.tight_layout()  # Adjust layout to fit everything
    plt.show()
else:
    print("No data to plot.")
