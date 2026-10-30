import os
import requests
from dotenv import load_dotenv
from config import get_api_key

load_dotenv()

JINA_API_KEY = get_api_key("JINA_API_KEY")


def rerank_documents(query, documents, top_n=5):

    if not documents:
        return []

    url = "https://api.jina.ai/v1/rerank"

    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json"
    }

    document_texts = [
        doc.page_content for doc in documents
    ]

    payload = {
        "model": "jina-reranker-v2-base-multilingual",
        "query": query,
        "documents": document_texts,
        "top_n": min(top_n, len(documents))
    }

    response = requests.post(
        url,
        headers=headers,
        json=payload,
        timeout=60
    )

    response.raise_for_status()

    results = response.json()["results"]

    reranked_documents = []

    for result in results:
        doc = documents[result["index"]]

        reranked_documents.append({
            "document": doc,
            "score": result["relevance_score"]
        })

    return reranked_documents