import os
from qdrant_client import QdrantClient

api_key: str = "replace_with_a_strong_random_secret"

client = QdrantClient(
    url="http://0.0.0.0:6333",
    api_key=api_key,
)

# List all collections
collections = client.get_collections()

if len (collections.collections) == 0:
    print("no collection exists")
else:
    for collection in collections.collections:
        print(collection.name)