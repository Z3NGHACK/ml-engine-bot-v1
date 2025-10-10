from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv('MONGODB_URI'))
db = client.crypto_trading

# Count BTC documents
btc_count = db.marketdatas.count_documents({'symbol': 'BTC'})
print(f"BTC documents: {btc_count}")

# Get oldest and newest
oldest = db.marketdatas.find_one({'symbol': 'BTC'}, sort=[('timestamp', 1)])
newest = db.marketdatas.find_one({'symbol': 'BTC'}, sort=[('timestamp', -1)])

print(f"Oldest: {oldest['timestamp']}")
print(f"Newest: {newest['timestamp']}")

# Calculate days of data
if oldest and newest:
    time_diff = newest['timestamp'] - oldest['timestamp']
    days = time_diff.total_seconds() / 86400
    print(f"Days of data: {days:.2f}")