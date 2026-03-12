from typing import List, Dict
from app.rag import search_similar_documents


def keyword_search(query: str, top_k: int = 5) -> List[Dict]:
    """
    Perform keyword-based search on legal documents.
    Uses FAISS semantic search to find relevant cases.
    """
    results = search_similar_documents(query, top_k)
    
    # Format results for search endpoint
    formatted_results = []
    for doc in results:
        formatted_results.append({
            "title": doc.get("title", "N/A"),
            "court": doc.get("court", "N/A"),
            "date": doc.get("date", "N/A"),
            "summary": doc.get("text", "")[:300] + "..." if len(doc.get("text", "")) > 300 else doc.get("text", ""),
            "full_text": doc.get("text", ""),
            "score": doc.get("score", 0.0),
            "source": doc.get("source", "Unknown")
        })
    
    return formatted_results
