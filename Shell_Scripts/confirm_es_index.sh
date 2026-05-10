#!/bin/bash

# To get the count of documents in the Elasticsearch index
# We can use this to verify that the data is being ingested by Logstash
# We can also use this to verify that the data is being ingested by Logstash

#Host details
HOST="elasticsearch"
PORT="9200"

#Printing the host details
echo $HOST:$PORT

#Get response from Elasticsearch
RESPONSE=$(curl -s "http://$HOST:$PORT/aladdin-logs-*/_count")
# ↑ $HOST = "elasticsearch" (Docker container name, not localhost)
# ↑ $PORT = "9200"
# ↑ aladdin-logs-* = wildcard matching all dated indices (e.g. aladdin-logs-2026.05.09)
# ↑ _count = Elasticsearch endpoint that returns document count

#Check if we got any response
echo "Checking for success message..."


if [ -z "$RESPONSE" ]; then
    echo "Got no response from Elasticsearch"
    exit 1 
fi

COUNT=$(echo "$RESPONSE" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d[\"count\"])")

echo "Elasticsearch trade count: $COUNT"

exit 0
