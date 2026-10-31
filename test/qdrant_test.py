from qdrant_client import QdrantClient

from diagnostic_settings import QdrantDiagnosticSettings

settings = QdrantDiagnosticSettings()

client = QdrantClient(
    url=str(settings.url),
    api_key=settings.api_key.get_secret_value(),
)

# List all collections
collections = client.get_collections()

if len(collections.collections) == 0:
    print("no collection exists")
else:
    for collection in collections.collections:
        print(collection.name)
