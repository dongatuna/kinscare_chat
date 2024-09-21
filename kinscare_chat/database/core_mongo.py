import os
import time
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from bson.objectid import ObjectId

RETRY_LIMIT = 3
RETRY_DELAY = 1  # in seconds

class MongoDbSession:

    def __init__(self, pref):
        self.pref = pref
        self.load_config()
        self.new_conn()

    def load_config(self):
        self.config = {
            'mongodb_uri': os.getenv('MONGODB_URI'),
            'db_name': os.getenv('MONGODB_DB_NAME'),
            'db_username': os.getenv('MONGODB_USERNAME'),
            'db_password': os.getenv('MONGODB_PASSWORD'),
            'auth_source': os.getenv('MONGODB_AUTH_SOURCE', 'admin')
        }

    def new_conn(self):
        try:
            self.client = MongoClient(
                self.config['mongodb_uri'],
                username=self.config['db_username'],
                password=self.config['db_password'],
                authSource=self.config['auth_source'],
                connectTimeoutMS=60000,
                serverSelectionTimeoutMS=60000,
                appname=self.pref
            )
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            self.db = self.client[self.config['db_name']]
        except ConnectionFailure as e:
            print(f"Could not connect to MongoDB: {e}")
            os._exit(1)

    def do(self, query_type, collection_name='', query=None, data=None, projection=None, update=None):
        attempt = 0
        while attempt < RETRY_LIMIT:
            try:
                return self._process(
                    query_type=query_type,
                    collection_name=collection_name,
                    query=query,
                    data=data,
                    projection=projection,
                    update=update
                )
            except ConnectionFailure as err:
                attempt += 1
                print(
                    f"Connection lost. Attempting to reconnect... "
                    f"(Attempt {attempt}/{RETRY_LIMIT})"
                )
                time.sleep(RETRY_DELAY)  # Delay before retrying
                self.new_conn()
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                raise
        print("Reached the maximum number of retries for reconnection. Exiting.")
        os._exit(1)

    def _process(self, query_type, collection_name='', query=None, data=None, projection=None, update=None):
        collection = self.db[collection_name]
        if query_type == 'select':
            return self._select(collection, query, projection)
        elif query_type == 'select_one':
            return self._select_one(collection, query, projection)
        elif query_type == 'select_exists':
            return self._select_exists(collection, query)
        elif query_type == 'insert':
            return self._insert(collection, data)
        elif query_type == 'update':
            return self._update(collection, query, update)
        elif query_type == 'delete':
            return self._delete(collection, query)
        else:
            raise Exception(f"Invalid query type passed: {query_type}")

    def _select(self, collection, query, projection):
        res = collection.find(query, projection)
        return list(res)

    def _select_one(self, collection, query, projection):
        res = collection.find_one(query, projection)
        return res

    def _select_exists(self, collection, query):
        count = collection.count_documents(query, limit=1)
        return count > 0

    def _insert(self, collection, data):
        result = collection.insert_one(data)
        return result.inserted_id

    def _update(self, collection, query, update):
        result = collection.update_one(query, update)
        return result.modified_count

    def _delete(self, collection, query):
        result = collection.delete_one(query)
        return result.deleted_count
