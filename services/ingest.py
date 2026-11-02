from utils.document_read import document_read
from models.embedding_model import embedding_model
from database.Milvus.Milvus_client import client
from config import COLLECTION_NAME
from config import KNOWLEDGE_FILE
from database.Milvus.Milvus_client import create_collection

def ingest_knowledge():
    chunks = document_read()

    text = [
        chunk.page_content for chunk in chunks
    ]

    vectors = embedding_model.embed_documents(text)

    data = [
        {
            "id":i,
            "vector":vectors[i],
            "text":text[i],
            "source":KNOWLEDGE_FILE,
            "chunk_id":i
        }for i in range(len(vectors))
    ]

    create_collection()


    upsert_res = client.upsert(
        collection_name = COLLECTION_NAME,
        data =data
    )

    print(f"insert results :{upsert_res}")

    client.flush(collection_name = COLLECTION_NAME)

    stats = client.get_collection_stats(COLLECTION_NAME)
    print(stats)

if __name__ == "__main__":
    ingest_knowledge()