import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    persist_directory="chroma_db",
    is_persistent=True
))

collection = client.get_or_create_collection(name="lost_items")


def add_to_vector_db(item_id, embedding):
    collection.add(
        ids=[str(item_id)],
        embeddings=[embedding]
    )


def search_vector_db(query_embedding):
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=1
    )
    return results
