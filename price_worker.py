# This is a simple Python script that fetches live stock prices from Yahoo Finance
# and stores them in Redis.
# This script is run in the background using docker-compose.
# It uses a while loop to continuously fetch prices and update Redis.
# It uses a try-except block to handle errors.
# It uses a time.sleep() to pause the loop for 12 seconds so we don't get banned by yahoo finance, in between that 12 seconds all requests for trading will be served the old price and will only be updated after 12 seconds.
# This is a trade-off between the accuracy of the price and the number of requests sent to yahoo finance.
# The higher the frequency of requests, the more accurate the price will be, but the higher the chance of getting banned by yahoo finance.
# The lower the frequency of requests, the lower the chance of getting banned by yahoo finance, but the lower the accuracy of the price.

import yfinance as yf
import redis
import time

# 1. Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 2. Define the "Universe" of stocks we want to track
STOCK_UNIVERSE = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS",
    "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "LT.NS", "BAJFINANCE.NS",
    "HINDUNILVR.NS", "AXISBANK.NS", "KOTAKBANK.NS", "ASIANPAINT.NS", "BAJAJFINSV.NS",
    "MARUTI.NS", "TITAN.NS", "SUNPHARMA.NS", "TATASTEEL.NS", "M&M.NS",
    "WIPRO.NS", "HCLTECH.NS", "ULTRACEMCO.NS", "NTPC.NS", "NESTLEIND.NS",
    "POWERGRID.NS", "TECHM.NS", "ONGC.NS", "GRASIM.NS", "ADANIPORTS.NS",
    "HINDALCO.NS", "JSWSTEEL.NS", "INDUSINDBK.NS", "TATAMOTORS.NS", "DIVISLAB.NS",
    "CIPLA.NS", "ADANIENT.NS", "BAJAJ-AUTO.NS", "SBILIFE.NS", "HDFCLIFE.NS",
    "EICHERMOT.NS", "APOLLOHOSP.NS", "BRITANNIA.NS", "DRREDDY.NS", "TATACONSUM.NS",
    "COALINDIA.NS", "HEROMOTOCO.NS", "BPCL.NS", "UPL.NS", "SHREECEM.NS"
]

def fetch_and_cache_prices():
    """
    SCENARIO B: Proactive Background Worker
    This runs in an infinite loop. It fetches prices for all stocks in the universe
    and forcefully overwrites the data in Redis.
    """
    print("🤖 Price Worker Started. Press Ctrl+C to stop.")
    
    while True:
        for ticker in STOCK_UNIVERSE:
            try:
                # Fetch the live price from Yahoo Finance
                live_price = yf.Ticker(ticker).fast_info['last_price']
                
                # Save the price to Redis with a 12-second TTL
                redis_key = f"price:STOCK:{ticker}"
                redis_client.setex(redis_key, 21600, live_price)
                print(f"Updated {ticker}: ₹{live_price}")
                
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
                
        print("Waiting 12 seconds before next fetch...")
        # Pause the loop for 12 seconds so we don't get banned!
        time.sleep(12)

if __name__ == "__main__":
    fetch_and_cache_prices()
