#This script helps us retrieve the prices of the stocks from the Redis cache, which was stored by the price_worker.py script.
# It uses redis.Redis() to connect to the Redis server.
# It uses get() to retrieve the price of the stock from the Redis server.
# It uses decode_responses=True to decode the response from the Redis server.

import redis
import yfinance as yf 

# 1. Connect to Redis (Our In-Memory Cache)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_stock_price(ticker: str) -> float:
    """
    SCENARIO B: Proactive Cache Reader
    This function NEVER talks to the internet. It only asks Redis.
    It trusts that our Background Worker (price_worker.py) is keeping Redis updated.
    """
    redis_key = f"price:STOCK:{ticker}"
    
    # 1. Try to get the price from Redis
    cached_price = redis_client.get(redis_key)
    
    # 2. If it's not there, we fail fast (because the worker hasn't fetched it yet!)
    if cached_price is None:
        # Implementing lazy loading now if the ticker price is not cached
        print(f"[CACHE MISS] Fetching {ticker} directly from the API now")
        stock = yf.Ticker(ticker)
        live_price = stock.fast_info['last_price']
        
        # Saving in redis for 300 seconds
        redis_client.setex(redis_key, 300, live_price)
        return float(live_price)

    print(f"[CACHE HIT] Served {ticker} from Redis instantly!")
    return float(cached_price)

# Test it out
if __name__ == "__main__":
    try:
        price = get_stock_price("RELIANCE.NS")
        print(f"Reliance Price: ₹{price}")
    except ValueError as e:
        print(f"Error: {e}")
