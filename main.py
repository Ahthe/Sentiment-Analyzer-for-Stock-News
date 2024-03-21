from flask import Flask, render_template, request, url_for
import pandas as pd
import plotly.express as px
from datetime import datetime
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import concurrent.futures

app = Flask(__name__)

# Constants
FINVIZ_URL = 'https://finviz.com/quote.ashx?t='
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    tickers = request.form['tickers'].split(',')
    tickers = [ticker.strip().upper() for ticker in tickers]

    # Fetch and parse data concurrently
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(fetch_html, ticker): ticker for ticker in tickers}
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

    # Check if pivot_df is empty
    if pivot_df.empty:
        return render_template('result.html', plot_html='<p>No data to plot.</p>')

    # Melt the DataFrame to convert it into a suitable format for animation
    melted_df = pd.melt(pivot_df.reset_index(), id_vars='date', value_vars=tickers, var_name='Ticker', value_name='Sentiment')

    # Create an animated bar chart using Plotly
    fig = px.bar(melted_df, x='Ticker', y='Sentiment', color='Ticker', animation_frame='date',
                 range_y=[-1, 1], title='Sentiment Analysis of Stock News')

    # Customize the layout
    fig.update_layout(
        xaxis=dict(title='Ticker'),
        yaxis=dict(title='Average Sentiment'),
        legend=dict(title='Ticker', orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        hovermode='x',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Add hover information
    fig.update_traces(hovertemplate='Ticker: %{x}<br>Sentiment: %{y:.2f}')

    # Gradient Colors
    colors = px.colors.sequential.Viridis
    fig.update_traces(marker=dict(color=colors, colorscale='Viridis', line=dict(width=2, color='white')))

    # Dynamic Title and Subtitle
    def update_title(frame):
        date = frame['data'][0]['name']
        return f'Sentiment Analysis of Stock News<br><span style="font-size:20px;">Date: {date}</span>'

    fig.update_layout(title=dict(text=update_title(fig.frames[0]), y=0.95, x=0.5, xanchor='center', yanchor='top', font=dict(size=24)))

    # Animated Markers
    def update_markers(frame):
        date = frame['data'][0]['name']
        sentiment_values = melted_df[melted_df['date'] == date]['Sentiment']
        markers = {}
        for ticker, sentiment in zip(melted_df[melted_df['date'] == date]['Ticker'], sentiment_values):
            if sentiment >= 0:
                markers[ticker] = dict(symbol='star', size=10, color='green')
            else:
                markers[ticker] = dict(symbol='circle', size=10, color='red')
        return markers

    fig.update_traces(marker=update_markers(fig.frames[0]))

    # Background Image
    fig.update_layout(images=[dict(source='https://example.com/background.jpg', xref='paper', yref='paper', x=0, y=0, sizex=1, sizey=1, sizing='stretch', layer='below')])

    # Smooth Transitions
    fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1000
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 500
    fig.layout.updatemenus[0].buttons[0].args[1]['transition']['easing'] = 'cubic-in-out'

    # Generate the plot HTML
    plot_html = fig.to_html(full_html=False)

    return render_template('result.html', plot_html=plot_html)

if __name__ == '__main__':
    app.run(debug=True)