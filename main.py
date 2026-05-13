from fastapi import FastAPI
from pydantic import BaseModel
from confluent_kafka import Producer
from market_data import get_live_price
import json

#following the singleton pattern, we connect to Postgres server, and since this is expensive, we do it at the startup
db.conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="[PASSWORD]",
    host="localhost",
    port="5432"
)

#For ACID transactions we turn the autocommit off, so that we can commit only when every transaction is successful, otherwise we roll back
db_conn.autocommit = False

app = FastAPI()

# 1. Build the Singleton Megaphone ONCE when the app starts, means create one expensive object once and then keep using as many times as needed
config = {
    'bootstrap.servers': 'localhost:9092',
    'socket.timeout.ms': 5000,
    'message.timeout.ms': 5000,
}
kafka_producer = Producer(config)

# 2. Tell FastAPI exactly what a "Trade Request" from the dashboard should look like
class TradeRequest(BaseModel):
    user_id: int
    ticker: str
    quantity: int
    action: str

@app.get("/")
def home():
    return {"message": "Aladdin_Lite API is running!"}

@app.get("/health")
def health_check():
    return {"status": "Aladdin_Lite is healthy"}

# 3. Create the HTTP POST Endpoint for the Dashboard
@app.post("/trade")
def execute_trade(trade: TradeRequest):
    # 'trade' is an object. Convert it to a dictionary so we can make it JSON
    trade_dict = trade.model_dump()
    # for kafka we again take the json data and then convert it into bytes with the encode method
    traded_data = json.dumps(trade_dict).encode('utf-8')

    # Delivery callback: prints success or exact error to the FastAPI terminal
    def on_delivery(err, msg):
        if err:
            print(f"[KAFKA ERROR] Delivery failed: {err}")
        else:
            print(f"[KAFKA OK] Message delivered to {msg.topic()} partition {msg.partition()}")

    kafka_producer.produce('market-trades', value=traded_data, on_delivery=on_delivery)
    kafka_producer.flush(5)  # Timeout after 5 seconds instead of hanging forever

    return {"status": "Success", "message": f"Sent {trade.quantity} shares of {trade.ticker} to Kafka!"}
