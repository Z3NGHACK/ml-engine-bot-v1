from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

uri = os.getenv('MONGODB_URI')
print(f"Testing connection with URI: {uri[:50]}...")

try:
    client = MongoClient(uri)
    
    # List all databases
    print("\n📊 Available databases:")
    for db_name in client.list_database_names():
        print(f"  - {db_name}")
    
    # Try crypto_trading database
    db_names = ['crypto_trading', 'cryptoTrading', 'test', 'crypto']
    
    for db_name in db_names:
        db = client[db_name]
        collections = db.list_collection_names()
        if collections:
            print(f"\n✅ Found data in '{db_name}':")
            for coll in collections:
                count = db[coll].count_documents({})
                print(f"  - {coll}: {count} documents")
                
                if coll == 'marketdatas' and count > 0:
                    # Check BTC specifically
                    btc_count = db[coll].count_documents({'symbol': 'BTC'})
                    print(f"    └─ BTC: {btc_count} documents")
    
    client.close()
    print("\n✅ Connection successful!")

except Exception as e:
    print(f"\n❌ Connection failed: {e}")
    