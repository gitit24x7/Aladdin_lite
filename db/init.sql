-- =====================================================
-- Aladdin Lite — Database Schema Initialization
-- Run once on first startup via Airflow or manually.
-- =====================================================

-- Users Table

CREATE TABLE IF NOT EXISTS users (
    id          SERIAL        PRIMARY KEY,
    username    VARCHAR(50)   NOT NULL UNIQUE,
    password    VARCHAR(255)  NOT NULL,
    email       VARCHAR(50)   NOT NULL UNIQUE,
    created_at  TIMESTAMP     DEFAULT NOW(),
    Balance     NUMERIC(15,2) DEFAULT 1000000
);

-- 1. Trades table — every order that comes through FastAPI lands here
CREATE TABLE IF NOT EXISTS trades (
    trade_id    SERIAL        PRIMARY KEY,
    user_id     INTEGER       NOT NULL REFERENCES users(id),
    ticker      VARCHAR(10)   NOT NULL,
    quantity    INTEGER       NOT NULL,
    price       NUMERIC(12,4) NOT NULL,          -- NUMERIC for financial precision (no float rounding errors)
    trade_time  TIMESTAMP     NOT NULL,
    status      VARCHAR(20)   DEFAULT 'PENDING', -- PENDING | VALID | REJECTED
    created_at  TIMESTAMP     DEFAULT NOW(),
    asset_type  VARCHAR(10)   NOT NULL,
    side        VARCHAR(10)   NOT NULL
);

CREATE TABLE IF NOT EXISTS portfolio (
    portfolio_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    ticker VARCHAR(10) NOT NULL,
    quantity INTEGER NOT NULL,
    avg_price NUMERIC(12,4) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    asset_type VARCHAR(10) NOT NULL,
    UNIQUE (user_id, ticker)
);


-- 2. Risk metrics table — nightly batch risk report written by Airflow
CREATE TABLE IF NOT EXISTS risk_metrics (
    id              SERIAL        PRIMARY KEY,
    report_date     DATE          NOT NULL,
    ticker          VARCHAR(10),
    total_quantity  INTEGER,                     -- total shares held across all trades
    total_exposure  NUMERIC(16,4),               -- total_quantity × avg_price
    risk_flag       VARCHAR(20),                 -- NORMAL | HIGH_RISK
    created_at      TIMESTAMP     DEFAULT NOW()
);

INSERT INTO users (username, password, email, balance) VALUES ('Admin_Aditya', 'secret', ' admin@gmail.com', 1000000);

-- 3. Sample seed data — so Airflow DAGs have something to read on first run
INSERT INTO trades (user_id, asset_type, side, ticker, quantity, price, trade_time, status) VALUES
    (1, 'STOCK', 'BUY', 'TSLA', 100,  197.50, '2024-01-01 09:30:00', 'VALID'),
    (1, 'STOCK', 'BUY', 'AAPL', 50,   213.00, '2024-01-01 09:31:00', 'VALID'),
    (1, 'STOCK', 'BUY', 'NVDA', 200,  875.25, '2024-01-01 09:32:00', 'VALID'),
    (1, 'STOCK', 'SELL', 'TSLA', -30,  -5.00,  '2024-01-01 09:33:00', 'PENDING');

