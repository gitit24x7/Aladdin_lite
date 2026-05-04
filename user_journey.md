# The Aladdin User Journey (Step-by-Step Architecture Flow)

This document maps out exactly what happens under the hood when a user performs an action in our "Mini Aladdin" system. Understanding this flow is crucial because it dictates *why* we write the code we write.

---

## The Scenario: "The Buy Order"
**The User (John)** clicks a button on his terminal dashboard to **Buy 50 shares of Apple (AAPL) for $150 each.**

Here is the exact microsecond-by-microsecond breakdown of what our code does.

---

### Step 1: The API Intake (FastAPI)
*   **Action:** The frontend dashboard sends an HTTP `POST` request to our FastAPI server (e.g., `/api/v1/trades`).
*   **What happens under the hood:** 
    *   Uvicorn (the server) receives the raw internet traffic and hands it to FastAPI.
    *   FastAPI routes it to our `create_trade()` Python function.
*   **Concepts to Byheart:** HTTP Methods (`GET` vs `POST`), Request Bodies (JSON).

### Step 2: Truth Validation (PostgreSQL)
*   **Action:** Before making the trade, our Python API asks a critical question: *Does John actually have $7,500 in cash to buy this?*
*   **What happens under the hood:** 
    *   Python uses an ORM (SQLAlchemy) to query the `users` table in our `aladdin_postgres` container.
    *   If John has the money, Python updates his PostgreSQL balance to deduct the $7,500 and creates a record in the `portfolios` table showing he now owns 50 shares of AAPL.
    *   *If he doesn't have the money*, Python stops here and returns a `400 Bad Request` error to the user.
*   **Concepts to Byheart:** Relational Databases, ACID Compliance, SQLAlchemy ORM syntax.

### Step 3: Broadcasting the Event (Kafka)
*   **Action:** The database is updated, but the rest of the company (Risk team, Analytics team) needs to know about this trade instantly.
*   **What happens under the hood:** 
    *   Python takes the transaction details (John, AAPL, 50 shares, $150) and packages it into a strict JSON dictionary.
    *   Python connects to the `aladdin_kafka` broker on port 9092.
    *   It publishes this JSON message to a Kafka topic called `market-trades`.
*   **Concepts to Byheart:** Kafka Producers, Topics, Brokers.

### Step 4: The Fast Response (FastAPI)
*   **Action:** Python tells John his trade went through.
*   **What happens under the hood:** 
    *   Because Python threw the message into Kafka and didn't wait for anyone else to process it, it can instantly send an HTTP `200 OK` back to John.
    *   John's screen shows "Success!" in less than 50 milliseconds.
*   **Concepts to Byheart:** Asynchronous programming, decoupling architecture.

---
*(At this exact microsecond, John is happy and moving on with his day. But deeply in the background, Kafka is distributing his trade to two entirely different systems simultaneously.)*
---

### Step 5: The Analytics Branch (Logstash -> Elasticsearch -> Kibana) 
*   **Action:** The data team needs this trade recorded for charting.
*   **What happens under the hood:** 
    *   **Logstash** is permanently listening to the `market-trades` Kafka topic.
    *   It hears the "John bought AAPL" message.
    *   It intercepts it (The **Filter** we will write), formats the timestamp perfectly, and forwards it to **Elasticsearch**.
    *   Elasticsearch saves it permanently.
    *   A completely separate Risk Manager is looking at **Kibana**. Kibana queries Elasticsearch, and the Risk Manager instantly sees a live bar chart spike up showing increased AAPL trading volume.
*   **Concepts to Byheart:** ELK pipelines, unstructured searching vs relational databases.

### Step 6: The Risk Engine Branch (The Python Worker)
*   **Action:** John just changed his portfolio. We must recalculate his financial risk (Is he now too heavily invested in Tech?).
*   **What happens under the hood:** 
    *   We have a *completely separate* Python script (The Risk Engine Worker) running in the background. It is also listening to the `market-trades` Kafka topic.
    *   It hears the trade. It loads John's *entire* updated portfolio from PostgreSQL.
    *   It feeds John's portfolio into our Open Source Mathematical Library (e.g., PyPortfolioOpt or QuantLib).
    *   The math library crunches the numbers and realizes John's portfolio volatility just skyrocketed.
    *   The Risk Engine updates John's `risk_score` in PostgreSQL from a `4` to an `8`.
*   **Concepts to Byheart:** Kafka Consumers, Background Workers, Open-source Library integration.

### Step 7: The Final State
*   John logs out, knowing his trade is secure in **PostgreSQL**.
*   The Risk Engine has mathematically proven his portfolio is now highly volatile, saving that metric back to **PostgreSQL**.
*   The Data Science team has a permanent, searchable timestamp of the exact trade in **Elasticsearch** for auditing and visualizations.

---

## How to use this document:
Whenever we start writing a new Python file or a new Logstash configuration, I will point to exactly which **Step (1 through 6)** we are currently building, so you never lose the "big picture."
