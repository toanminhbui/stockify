import os
import requests
from datetime import datetime, timedelta
# import matplotlib.pyplot as plt
from groq import Groq
import yfinance as yf
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(dotenv_path='.env.local')
# Install required libraries
# pip install yfinance groq pandas matplotlib requests
app = FastAPI()
# Set up API keys (replace with your actual keys)
NEWS_API_KEY = os.getenv('NEWS_API_KEY')


origins = [
    "http://localhost:3000",  # React development server
    # Your production domain
    "https://smart-thoughts-mmm84xfit-toanminhbuis-projects.vercel.app/",
    "https://smart-thoughts.vercel.app",
    "https://smart-thoughts.vercel.app/brainstore",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class stockNews(BaseModel):
    ticker: str
    newsType: str 
# Initialize Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

def get_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="1mo")
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def analyze(symbol, summary):
    data_for_analysis = f"""
    Stock Symbol: {symbol}

    Recent analyses:
    {summary}

    Please provide a brief analysis of the stock's market news.
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
        return response.choices[0].message.content
    except Exception as e:
        analysis = f"Could not retrieve analysis: {str(e)}"

@app.get("/api/news")
def get_news(stock: stockNews):
    symbol = stock.ticker
    newsType = stock.newsType
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # Create a more specific search query
    company_name = yf.Ticker(symbol).info.get('longName', symbol)
    query = f'"{symbol}" stock'
    specifiedType = ""
    if newsType != "none":
        specifiedType = f"%20T:{newsType}" 
    url = f"https://api.tickertick.com/feed?q=(and%20tt:{symbol}%20{specifiedType})&n=10"
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


@app.get("/api/analyze")
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
    stockData = stockNews(newsType="none", ticker=symbol)
    marketData = stockNews(newsType="market", ticker=symbol)
    # SecData = stockNews(newsType="sec", ticker=symbol)

    news = get_news(stockData)
    market = get_news(marketData)
    # sec = get_news(SecData)
    market_summary = news_summary = "\n".join([f"- {article['title']}" for article in market])
    ai_market_analyze = analyze(symbol, market_summary)
    news_summary = "\n".join([f"- {article['title']}" for article in news])
    title = "\n".join([f"- {article['title']}" for article in news])
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
        "current_price": round(current_price,2),
        "price_change": round(price_change,2),
        "percent_change": round(percent_change,2),
        "analysis": analysis,
        "market_sentiment": ai_market_analyze,
        # "sec": sec
    }

