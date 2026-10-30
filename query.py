
import os
from dotenv import load_dotenv
from reranker import rerank_documents
from langchain_pinecone import (
    PineconeEmbeddings,
    PineconeVectorStore
)
from config import get_api_key

load_dotenv()

# Connect to the embedding model
embeddings_model = PineconeEmbeddings(
    model="multilingual-e5-large",
    pinecone_api_key=get_api_key("PINECONE_API_KEY")
)

# Connect to the clean Pinecone index
vector_store = PineconeVectorStore.from_existing_index(
    index_name="corp-docs-rag-clean",
    embedding=embeddings_model
)

# Create a retriever
retriever = vector_store.as_retriever(
    search_kwargs={"k": 20}
)


def retrieve_and_rerank(query):
    # Retrieve the top 20 chunks
    documents = retriever.invoke(query)

    print("Retrieved:", len(documents))

    # Rerank and keep the top 5
    results = rerank_documents(
        query=query,
        documents=documents,
        top_n=5
    )

    return results


if __name__ == "__main__":
    query = input("Ask a question: ")

    results = retrieve_and_rerank(query)

    for i, item in enumerate(results, start=1):
        doc = item["document"]

        print(f"\n--- Reranked Chunk {i} ---")
        print("Relevance score:", item["score"])
        print("Source:", doc.metadata.get("source"))
        print(doc.page_content[:500])