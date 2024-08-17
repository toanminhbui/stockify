import os
import requests
from datetime import datetime, timedelta
import pandas as pd
# import matplotlib.pyplot as plt
from groq import Groq
import yfinance as yf
from fastapi import FastAPI
from pydantic import BaseModel
# Install required libraries
# pip install yfinance groq pandas matplotlib requests
app = FastAPI()
# Set up API keys (replace with your actual keys)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

class stockNews(BaseModel):
    ticker: str
    newsType: str
# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="1mo")
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
@app.get("/news")
def get_news(symbol):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Create a more specific search query
    company_name = yf.Ticker(symbol).info.get('longName', symbol)
    query = f'"{symbol}" stock'

    url = f"https://api.tickertick.com/feed?q=(and%20tt:{symbol}%20)&n=100"
    response = requests.get(url)
    data = response.json()
    if "stories" not in data:
        print("stories not found")
        return []
    
    # Filter articles to ensure they are relevant to the stock
    relevant_articles = []
    for article in data["stories"]:
        title = article['title'].lower()
        description = article.get('description', '').lower()
        url = article.get('url', '').lower()


        relevant_articles.append(
            {
                "title": title,
                "description": description,
                "url": url,
            }
        )


    return relevant_articles  # Return up to 5 relevant news articles
@app.get("/analyze")
def analyze_stock(symbol: str):
    df = get_stock_data(symbol)
    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"Error: Unable to fetch data for {symbol}")

    recent_data = df.tail(30)
    current_price = recent_data.iloc[-1]["Close"]
    price_change = current_price - recent_data.iloc[-2]["Close"]
    percent_change = (price_change / recent_data.iloc[-2]["Close"]) * 100

    # plt.figure(figsize=(12, 6))
    # plt.plot(recent_data.index, recent_data["Close"])
    # plt.title(f"{symbol} Stock Price - Last 30 Days")
    # plt.xlabel("Date")
    # plt.ylabel("Price")
    # plt.xticks(rotation=45)
    # plt.tight_layout()
    # chart_filename = f"{symbol}_stock_chart.png"
    # plt.close()

    news = get_news(symbol)
    news_summary = "\n".join([f"- {article['title']}" for article in news])
    title = "\n".join([f"- {article['title']}" for article in news])
    print(news_summary)
    data_for_analysis = f"""
    Stock Symbol: {symbol}
    Current Price: ${current_price:.2f}
    Price Change: ${price_change:.2f}
    Percent Change: {percent_change:.2f}%

    Recent analyses:
    {news_summary}

    Please provide a brief analysis of the stock's performance and potential factors affecting its price.
    """

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an unbiased expert financial analyst providing insights on stock performance.",
                },
                {
                    "role": "user",
                    "content": data_for_analysis,
                },
            ],
            model="mixtral-8x7b-32768",
            temperature=0.5,
            max_tokens=300,
        )

        analysis = response.choices[0].message.content

    except Exception as e:
        analysis = f"Could not retrieve analysis: {str(e)}"

    return {
        "symbol": symbol,
        "current_price": current_price,
        "price_change": price_change,
        "percent_change": percent_change,
        "analysis": analysis,
    }

