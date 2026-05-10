import yfinance as yf
import redis
import time

# 1. Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 2. Define the "Universe" of stocks we want to track
# For testing, we just track 3 popular stocks
STOCK_UNIVERSE = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]

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
                # STEP 1: Fetch the live price from Yahoo Finance
                # WRITE YOUR CODE HERE (use yf.Ticker)
                # live_price = ...
                
                # STEP 2: Save the price to Redis with a 15-second TTL
                redis_key = f"price:STOCK:{ticker}"
                # WRITE YOUR CODE HERE (use redis_client.setex)
                
                # print(f"Updated {ticker}: ₹{live_price}")
                pass # remove this pass when you write your code
                
            except Exception as e:
                print(f"Error fetching {ticker}: {e}")
                
        print("Waiting 12 seconds before next fetch...")
        # STEP 3: Pause the loop for 12 seconds so we don't get banned!
        # WRITE YOUR CODE HERE (use time.sleep)
        

if __name__ == "__main__":
    fetch_and_cache_prices()
