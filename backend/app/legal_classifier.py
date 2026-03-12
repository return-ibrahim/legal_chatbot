import re

def classify_legal_query(query: str) -> str:
    """Classify query to route to correct legal index/filter"""
    q = query.lower()

    # 1. Statute (Section specific)
    # Matches: "Section 302", "IPC 302", "Article 21", "u/s 420"
    if re.search(r'\b(section|sec|u/s|article)\b', q) or \
       re.search(r'\b(ipc|crpc|bns|bnss)\b', q):
        if "vs" not in q and "v." not in q: # Ensure it's not a case title like "State vs 302"
            return "statute"

    # 2. Comparison
    if "compare" in q or "difference" in q or "versus" in q:
        return "comparison"

    # 3. Judgment / Case Law
    # Matches: "State vs", "Kesavananda case", "landmark judgment"
    if any(word in q for word in ["case", "judgment", "landmark", "vs", "v.", "court held", "ruling"]):
        return "judgment"

    # 4. Concept Explanation
    # Matches: "What is FIR", "Meaning of bail", "Define murder"
    if any(word in q for word in ["what is", "meaning", "define", "explain", "concept", "principle"]):
        return "concept"

    # 5. Situational Advice
    # Matches: "Can I", "Is it legal", "Legal action"
    if any(word in q for word in ["can i", "can police", "legal action", "is it legal", "what can i do", "remedy"]):
        return "advice"

    return "general"
