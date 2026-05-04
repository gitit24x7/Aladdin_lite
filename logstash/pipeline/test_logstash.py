#script to connect to localhost 5000 over standard tcp and send a json string 
# to send {"ticker": "AAPL", "quantity": "50", "trade_time": "2026-04-24T12:00:00Z"}

import socket
import json

# Create a TCP socket
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
socket.connect(("localhost", 5000))

# Send a JSON string
socket.sendall((json.dumps({"ticker": "AAPL", "quantity": "50", "trade_time": "2026-04-24T12:00:00Z"}) + "\n").encode())

# Close the connection
socket.close()