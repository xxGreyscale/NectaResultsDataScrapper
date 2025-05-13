from pymongo import MongoClient

_client: MongoClient | None = None  # Keep the client instance at the module level


def get_db_client(connection_string: str) -> MongoClient:
    """
    Returns a MongoClient instance.  Creates one if it doesn't exist,
    otherwise returns the existing one.
    """
    global _client
    if _client is None:
        try:
            _client = MongoClient(connection_string)
            _client.admin.command('ping')  # Check the connection
            print("Successfully connected to MongoDB!")
        except ConnectionError as e:
            print(f"Error connecting to MongoDB: {e}")
            raise  # Re-raise the exception to signal failure
    return _client


def get_database(connection_string: str, db_name: str):
    """
    Returns a database object from the MongoClient.
    """
    client = get_db_client(connection_string)  # Use the shared client
    return client[db_name]


def close_db_client():
    """
    Closes the MongoClient instance.  Call this when your application is shutting down.
    """
    global _client
    if _client:
        _client.close()
        print("MongoDB client connection closed.")
        _client = None  # Reset to None
