# This document was created for MongoDB Atlas,
# prior to migrating to a local instance of MongoDB 8.0.4.
# May be modified for local use.
from pymongo import MongoClient

# Connection URI
uri = "***REMOVED***"
client = MongoClient(uri)

# Access the database and collection
db = client["ModeledHomes"]
collection = db["plan_embeddings"]

# Create the vector index
result = collection.create_index(
    [("embedding", "knnVector")],  # Specify the field and type
    name="embedding_knnVector_index",  # Index name
    vectorDimensions=512,  # Dimensions of the vector
    similarity="cosine"  # Similarity method
)

print("Index created:", result)