from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

print("🔍 Starting MongoDB connection test...")

try:
    client = MongoClient(
        "mongodb+srv://bijaymstry:Ob0hqn0hidUbPhrM@cluster0.qewaugl.mongodb.net/?retryWrites=true&w=majority",
        serverSelectionTimeoutMS=5000,
        tls=True,
        tlsAllowInvalidCertificates=True  # Only for local testing
    )
    
    print("⏳ Pinging server...")
    info = client.server_info()  # This will raise an error if the connection fails
    print("✅ Connected! Server Info:")
    print(info)

except ServerSelectionTimeoutError as err:
    print("❌ Server selection timeout:", err)
except Exception as e:
    print("❌ Other error:", e)
