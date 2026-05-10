# Aladdin Lite - Architectural Decisions Log

This document tracks all major system design decisions made during the development of the Aladdin Lite platform, including the "First Principles" reasoning and the technical implementation details.

### 1. Relational State Management
**Decision:** Store user balances and portfolio holdings as "State Snapshots" rather than calculating them dynamically from event logs (trades).
**Reason:** If a user wants to view their portfolio, forcing the database to scan millions of historical trades and calculate the sum is extremely slow. A dedicated `portfolio` table allows instant dashboard loading.
**Implementation:** Created a `portfolio` table in PostgreSQL. Used a Composite Unique Constraint `UNIQUE (user_id, ticker)` to physically force the database to reject duplicate holding rows for the same stock, ensuring Python updates the quantity rather than inserting a new row.

### 2. Orphan Data Protection
**Decision:** Enforce strict relationships between Trades and Users at the database level.
**Reason:** To prevent the Python application from accidentally inserting trades for users that do not exist, which would cause dashboard crashes and corrupted analytics.
**Implementation:** Used a Foreign Key constraint `user_id INTEGER NOT NULL REFERENCES users(id)` in the `trades` table.

### 3. Rate Limit Protection (The Redis Shield)
**Decision:** Never allow the Trading Engine (FastAPI) to communicate directly with Yahoo Finance.
**Reason:** If 15 users spam the "Trade" button, it generates hundreds of API calls per second, which will trigger a permanent IP ban from Yahoo. Network I/O is also ~5,000x slower than Memory I/O.
**Implementation:** Introduced a Redis container. The FastAPI backend will only use `redis_client.get("price:STOCK:RELIANCE.NS")` to fetch prices from RAM in 0.1 milliseconds.

### 4. Proactive Background Fetching (The Worker)
**Decision:** Run a continuous background script (`price_worker.py`) to fetch prices for a core "Universe" of stocks.
**Reason:** By detaching the price-fetching logic from the user's "Buy" button, users experience zero latency. The worker takes the penalty of network latency so the user doesn't have to.
**Implementation:** Created an infinite `while True:` loop that fetches prices and uses `time.sleep(12)` to strictly throttle our API requests to 5 times per minute, keeping us completely invisible to Yahoo's rate limiters.

### 5. Cache Invalidation and Expiration (TTL)
**Decision:** Cached prices must automatically self-destruct.
**Reason:** If the background worker crashes, Redis will continue holding the last known price. If a user buys a stock based on a frozen price from 3 days ago, the broker loses money.
**Implementation:** Implemented Time-To-Live (TTL) using `redis_client.setex(redis_key, 15, live_price)`. Because the worker loops every 12 seconds, a 15-second TTL ensures data is either fresh or completely deleted.

### 6. Stealth Data Fetching
**Decision:** Use undocumented API endpoints rather than standard Web Scraping payloads.
**Reason:** Standard endpoints like `stock.info` force Yahoo to send a massive JSON file containing CEO names, PE ratios, and addresses. Requesting this payload every 12 seconds triggers bot-protection.
**Implementation:** Replaced `.info["currentPrice"]` with `.fast_info['last_price']`, which hits a lightweight endpoint designed for Yahoo's live charts, downloading only a few bytes.

### 7. The Hybrid Cache Strategy
**Decision:** Allow the Trading Engine (`market_data.py`) to act as a fallback "Lazy Cache".
**Reason:** The background worker can only track the Top 50 stocks without getting banned. If a user requests an obscure stock, the system still needs to serve them.
**Implementation:** If `redis_client.get()` returns `None` (Cache Miss), `market_data.py` catches it, fetches the price directly from `yfinance`, executes the trade, and saves it to Redis for 5 minutes (`setex`) so the next user gets it instantly.

### 8. Order Book vs Market Maker
**Decision:** Do not build a Matching Engine / Order Book.
**Reason:** Building an exchange requires users to take the opposite side of every trade, which is immensely complex (handling bid-ask spreads, partial fills, queueing).
**Implementation:** We built a "Paper Trading Broker". We assume infinite market liquidity. If the global price is ₹1500, we instantly create the stock out of thin air and deduct the cash balance.
