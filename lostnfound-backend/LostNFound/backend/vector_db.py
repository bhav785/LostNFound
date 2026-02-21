import chromadb
from chromadb.config import Settings

client = chromadb.Client(Settings(
    persist_directory="chroma_db",
    is_persistent=True
))

lost_collection = client.get_or_create_collection(name="lost_items")
found_collection = client.get_or_create_collection(name="found_items")


def add_to_vector_db(item_id, embedding, is_lost=True):
    col = lost_collection if is_lost else found_collection
    col.add(
        ids=[str(item_id)],
        embeddings=[embedding],
        metadatas=[{"type": "lost" if is_lost else "found"}]
    )


def search_vector_db(query_embedding, search_lost=True):
    col = lost_collection if search_lost else found_collection
    results = col.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    return results
