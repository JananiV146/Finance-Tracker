#!/usr/bin/env python
"""Test MongoDB Atlas connection"""
import os
import certifi
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

uri = os.environ.get(
    "MONGODB_URI",
    "mongodb+srv://jananivenkatachalam14:jananivenkatachalam@userauthentication.iagkujk.mongodb.net/?retryWrites=true&w=majority&appName=userAuthentication"
)

print("=" * 60)
print("MONGODB CONNECTION TEST")
print("=" * 60)
print(f"\nConnection URI: {uri[:80]}...")
print("\nAttempting to connect to MongoDB Atlas...\n")

try:
    # Try standard secure connection
    print("1️⃣  Trying standard secure connection (with certifi)...")
    client = MongoClient(uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    print("   ✅ SUCCESS! Connected with standard secure connection")
    
    # Get database info
    db = client.finance_tracker
    collections = db.list_collection_names()
    print(f"   📊 Database: finance_tracker")
    print(f"   📋 Collections: {collections if collections else 'None (empty database)'}")
    
    client.close()
    
except (ServerSelectionTimeoutError, ConnectionFailure) as e:
    print(f"   ❌ Standard connection failed")
    error_msg = str(e)
    if "DNS" in error_msg or "resolution" in error_msg:
        print("   → Issue: DNS resolution timeout (network connectivity problem)")
    elif "SSL" in error_msg or "handshake" in error_msg:
        print("   → Issue: SSL/TLS handshake failed")
    else:
        print(f"   → Issue: {error_msg[:100]}")
    
    print("\n2️⃣  Trying with tlsAllowInvalidCertificates (development mode)...")
    try:
        client = MongoClient(
            uri,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=5000
        )
        client.admin.command("ping")
        print("   ✅ SUCCESS! Connected with tlsAllowInvalidCertificates=True")
        
        # Get database info
        db = client.finance_tracker
        collections = db.list_collection_names()
        print(f"   📊 Database: finance_tracker")
        print(f"   📋 Collections: {collections if collections else 'None (empty database)'}")
        
        client.close()
    except Exception as e2:
        print(f"   ❌ Fallback connection also failed")
        print(f"   → Error: {str(e2)[:100]}")

except Exception as e:
    print(f"   ❌ Unexpected error: {str(e)[:200]}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
