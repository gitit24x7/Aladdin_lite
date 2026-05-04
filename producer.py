from confluent_kafka import Producer
import json

# 1. Configure the Producer to point to our local Kafka Broker
config = {
    'bootstrap.servers': 'localhost:9092'
}
producer = Producer(config)

# 2. The simulated JSON trade data from our User Journey
trade_data = {
    "ticker": "TSLA",
    "quantity": "100", 
    "trade_time": "2026-04-24T12:05:00Z"
}

#Translate the Dictionary to a JSON string, then to raw Bytes
payload_bytes = json.dumps(trade_data).encode('utf-8')


producer.produce('market-trades', value=payload_bytes)
#here market trades is a topic in Kafka or in more simpler language a channel too
#right now we are creating one dynamically on the go, but in production this does not happen and dynamic creations are banned 

producer.flush()
print("Trade sent to Kafka successfully!")



