# Sentiment Analyzer for Stock News 📈

Hey there! My name is Syed Ahthesham Ali I'm a recent CS graduate from University of Mount Union who's fascinated by the intersection of technology and finance. This project is a reflection of my journey learning web scraping and sentiment analysis—two powerful techniques that I believe can make a difference in the fast-paced world of stock investing. 🚀

Like many families, mine is interested in the stock market. But we often found ourselves overwhelmed by lengthy articles, and the sheer effort of discerning the market sentiment from them was pretty daunting. Enter the "Sentiment Analyzer for Stock News": a tool designed to cut through the noise and provide clear insights into market sentiment. 📰➡️😃 or 😟

## How It Helps
![Firefox_Screenshot_2024-03-21T06-04-05 496Z](https://github.com/Ahthe/Sentiment-Analyzer-for-Stock-News/assets/107819350/fce8d156-06c0-43ec-967d-d303ecf7d5d7)

This tool automates the grunt work of reading through numerous articles by:
- Scraping news headlines related to stocks of interest.
- Applying sentiment analysis to understand the general tone of the news.
- Visualizing the sentiment scores to indicate positive, neutral, or negative sentiment.

No more sifting through endless paragraphs. Now, getting the sentiment is just a matter of seconds. It's like having a personal financial analyst who reads everything and tells you, "Hey, this looks good!" or "Hmm, there might be some concerns here."

![Screenshot 2024-03-21 020307](https://github.com/Ahthe/Sentiment-Analyzer-for-Stock-News/assets/107819350/2bd16f89-374b-4081-ae1b-461d3ba9cb4c)

## Highlights

- Web scraping with `BeautifulSoup`:
  ```python
  req = Request(url=url, headers={'user-agent': USER_AGENT})
  response = urlopen(req)

- Sentiment analysis using `NLTK`:
  ```python
  vader = SentimentIntensityAnalyzer()
  df['compound'] = df['title'].apply(lambda title: vader.polarity_scores(title)['compound'])

- Data visualization with `Matplotlib`:
  ```python
  mean_df.plot(kind='bar', figsize=(10, 8))

# Setup

Setting up this tool is as easy as pie! 🍰

-  **Clone the repository**:
   ```sh
   git clone https://github.com/your-username/Sentiment-Analyzer-for-Stock-News.git

- Navigate to the project directory:
  ```sh
  cd Sentiment-Analyzer-for-Stock-News

- Install the required libraries:
  ```sh
  pip install pandas matplotlib beautifulsoup4 nltk
  
- Run the script:
```sh
  python sentiment_analyzer.py
