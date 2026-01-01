#!/usr/bin/env python3
"""Simple script to test if Notion API token is valid"""

from notion_client import Client

# Replace this with your actual API token
API_TOKEN = input("Enter your Notion API token (starts with ntn_): ").strip()
DATABASE_ID = input("Enter your database ID: ").strip()

try:
    client = Client(auth=API_TOKEN)

    # Test 1: Try to retrieve the database
    print("\n🧪 Test 1: Checking if token is valid and can access database...")
    db = client.databases.retrieve(DATABASE_ID)
    print(f"✅ Success! Database found: {db.get('title', 'Unknown')}")

    # Test 2: Try to create a simple page with just Title
    print("\n🧪 Test 2: Creating a test page with Title property only...")
    response = client.pages.create(
        parent={"database_id": DATABASE_ID},
        properties={
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": "Test page from CLI"
                        }
                    }
                ]
            }
        }
    )
    print(f"✅ Success! Page created with ID: {response['id']}")
    print(f"   URL: https://notion.so/{response['id']}")

except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nPossible issues:")
    print("1. API token is incorrect or expired")
    print("2. Integration is not shared with the database")
    print("3. Database ID is wrong")
