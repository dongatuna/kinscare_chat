# Kinscare Chat

## Deployment

- Google Cloud Run: https://console.cloud.google.com/run/detail/us-central1/dev-career-path-bot?project=kinscare
- Cloud SQL - PostgreSQL: https://console.cloud.google.com/sql/instances?project=kinscare

## MongoDB


### Auth

```
MONGODB_URI: The MongoDB URI (e.g., "mongodb://localhost:27017/")
MONGODB_DB_NAME: The name of your database
MONGODB_USERNAME: Your MongoDB username
MONGODB_PASSWORD: Your MongoDB password
MONGODB_AUTH_SOURCE (optional): Authentication database (default is 'admin')
```


### Inserting a document

```
from bson.objectid import ObjectId

# Insert a new user
data = {
    "ext_user_id": "external_user_123",
    "settings": {
        "share_emails": []
    }
}
user_id = write_db.do('insert', collection_name='users', data=data)
print(f"Inserted user with _id: {user_id}")
```

### Querying a Document

```
# Query a user by external user ID
query = {"ext_user_id": "external_user_123"}
user = read_db.do('select_one', collection_name='users', query=query)
print(user)
```

### Updating a document

```
# Update user settings
query = {"_id": ObjectId(user_id)}
update = {"$set": {"settings.share_emails": ["email@example.com"]}}
modified_count = write_db.do('update', collection_name='users', query=query, update=update)
print(f"Modified {modified_count} document(s)")
```

### Checking if a Document Exists

```
# Check if a user exists
query = {"ext_user_id": "external_user_123"}
exists = read_db.do('select_exists', collection_name='users', query=query)
print(f"User exists: {exists}")
```
