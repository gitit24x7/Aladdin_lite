#This script helps us retrieve the prices of the stocks from the Redis cache, which was stored by the price_worker.py script.

import redis

# 1. Connect to Redis (Our In-Memory Cache)
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_stock_price(ticker: str) -> float:
    """
    SCENARIO B: Proactive Cache Reader
    This function NEVER talks to the internet. It only asks Redis.
    It trusts that our Background Worker is keeping Redis updated.
    """
    redis_key = f"price:STOCK:{ticker}"
    
    # 1. Try to get the price from Redis
    cached_price = redis_client.get(redis_key)
    
    # 2. If it's not there, we fail fast (because the worker hasn't fetched it yet!)
    if cached_price is None:
        raise ValueError(f"Price for {ticker} not found in cache. Is the Price Worker running?")
        
    # 3. If it is there, return it instantly
    return float(cached_price)

# Test it out
if __name__ == "__main__":
    try:
        price = get_stock_price("RELIANCE.NS")
        print(f"Reliance Price: ₹{price}")
    except ValueError as e:
        print(f"Error: {e}")
