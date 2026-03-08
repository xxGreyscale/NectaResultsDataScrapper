from pymongo import MongoClient
from infastructure import settings

_client: MongoClient | None = None  # Keep the client instance at the module level


def get_db_client(connection_string: str | None = None) -> MongoClient:
    """
    Returns a MongoClient instance. Creates one if it doesn't exist.
    """
    global _client
    if _client is None:
        try:
            mongo_uri = connection_string or settings.MONGO_URI
            _client = MongoClient(mongo_uri)
            _client.admin.command('ping')
            print("Successfully connected to MongoDB!")
        except ConnectionError as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
    return _client


def get_database(connection_string: str | None = None, db_name: str | None = None):
    """
    Returns a database object from the MongoClient.
    """
    client = get_db_client(connection_string)
    database_name = db_name or settings.DB_NAME
    return client[database_name]


def close_db_client():
    """
    Closes the MongoClient instance.  Call this when your application is shutting down.
    """
    global _client
    if _client:
        _client.close()
        print("MongoDB client connection closed.")
        _client = None  # Reset to None
