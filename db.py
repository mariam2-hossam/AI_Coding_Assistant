import uuid
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection("knowledge")
model = SentenceTransformer("all-MiniLM-L6-v2")


def split_text(text, size=800):
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) > size and current:
            chunks.append(current)
            current = ""
        current += line + "\n"
    if current.strip():
        chunks.append(current)
    return chunks


def add_text(text, title, source):
    chunks = split_text(text)
    vectors = model.encode(chunks).tolist()
    ids = [str(uuid.uuid4()) for c in chunks]
    metas = [{"title": title, "source": source} for c in chunks]
    collection.add(ids=ids, documents=chunks, embeddings=vectors, metadatas=metas)
    return len(chunks)


def search(question, k=3):
    count = collection.count()
    if count == 0:
        return []
    vector = model.encode([question]).tolist()
    result = collection.query(query_embeddings=vector, n_results=min(k, count))
    return result["documents"][0]
