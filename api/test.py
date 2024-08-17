import os
import requests
from datetime import datetime, timedelta
import pandas as pd
# import matplotlib.pyplot as plt
from groq import Groq
import yfinance as yf
from fastapi import FastAPI
# Install required libraries
# pip install yfinance groq pandas matplotlib requests
app = FastAPI()
# Set up API keys (replace with your actual keys)
GROQ_API_KEY = "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"
NEWS_API_KEY = "32be840bda864baf93505020ca1fc407"

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

def get_news(symbol):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Create a more specific search query
    company_name = yf.Ticker(symbol).info.get('longName', symbol)
    query = f'"{symbol}" stock'

    url = f"https://api.tickertick.com/feed?q=z:{symbol}&n=5"
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

info = get_news("ba")
print(info)