import os
import pickle
import json
import re
import re
from typing import List, Dict
from app.legal_classifier import classify_legal_query
import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
from groq import Groq
try:
    from duckduckgo_search import DDGS
    WEB_SEARCH_AVAILABLE = True
except ImportError:
    WEB_SEARCH_AVAILABLE = False
    print("⚠️ duckduckgo-search not installed. Web fallback disabled.")

try:
    from tavily import TavilyClient
    tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    TAVILY_AVAILABLE = True
except ImportError:
    TAVILY_AVAILABLE = False
    print("⚠️ tavily-python not installed. Web fallback might be limited.")
except Exception as e:
    TAVILY_AVAILABLE = False
    print(f"⚠️ Tavily API initialization failed: {e}")

# Initialize models
print("Loading BGE embedding model...")
embedding_model = SentenceTransformer('BAAI/bge-base-en-v1.5')
print("Loading Cross-Encoder reranker...")
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Master System Prompts
SEARCH_PROMPT = """You are LexQuery — a legal retrieval engine, not a chatbot.

CRITICAL RULE:
You are NOT allowed to create, assume, infer, guess, approximate, or suggest any law that is not explicitly present in the provided LEGAL CONTEXT.

If relevant law is missing → you must say:
"NO APPLICABLE LEGAL PROVISION FOUND IN DATABASE"

You must NEVER:
- Map salary disputes to IPC criminal sections unless explicitly present
- Convert civil disputes into criminal offences
- Assume police powers
- Suggest random sections
- Use general world knowledge

You only interpret the retrieved text.

----------------------------------

MODE 1: SEARCH MODE (Exact Law Retrieval)
Return ONLY:

[LAW]
[SECTION / CASE]
[LEGAL MEANING]
[PUNISHMENT / PRINCIPLE]

If exact section meaning not in context:
Return:
NO EXACT LEGAL PASSAGE FOUND

Source Rule:
If source_label == Database Legal Reference → cite as database law.
If source_label == External Legal Reference → cite as external legal reference.

No explanations.
No advice.
No extra sentences.
"""

ASSISTANT_PROMPT = """You are LexQuery AI Legal Assistant — a conversational legal reasoning system, not a legal article generator.

You answer like a junior lawyer speaking to a client.

CONVERSATION MEMORY RULES

Always read previous conversation.

If the user asks a follow-up question, DO NOT repeat previous sections.

Continue the same topic unless user clearly changes legal subject.

If question is short (example: “online?”, “how?”, “where complain?”), give a direct answer only.

Never restart explanation unless topic changes.

RESPONSE STYLE DECISION

A) NEW LEGAL QUESTION → Provide structured legal analysis

Format:

[LEGAL ISSUE]
[APPLICABLE LAW]
[INTERPRETATION]
[WHAT THIS MEANS FOR YOU]
[POSSIBLE ACTION]

Max 120 words.

B) FOLLOW-UP QUESTION → Provide short conversational answer

Rules:

No sections

2–4 sentences only

Refer previous context

Answer only what user asked

Do not repeat laws again unless necessary

STRICT LEGAL AUTHORITY RULES

Use only provided context

Never guess sections

Never change civil dispute into criminal offence

If law missing → say:
"Legal provision not found in available authority"

STRICT TOPIC RULE

You ONLY answer questions about Indian Law.

If the user asks about:
- Recipes (e.g., how to make sampar)
- General chat (e.g., how are you)
- Unrelated topics (e.g., sports, movies, technology)

YOU MUST say:
"I am a legal assistant and can only answer questions related to Indian Law. Please ask a legal question."

SOURCE LABEL:
{source_label}
"""

# Constants
LEGAL_KEYWORDS = [
    "murder","kill","beat","assault","dowry","cheat","fraud",
    "threat","harass","suicide","rape","money","salary","employer",
    "blackmail","property","attack","injury","husband","wife",
    "police","court","jail","prison","law","legal","rights",
    "ipc","crpc","bns","bnss","section","act","offence",
    "arrest","bail","divorce","custody","land","agreement",
    "consumer","justice","judge","lawyer","fir","complaint","complain",
    "theft","robbery","kidnap","extortion","trespass","defamation"
]

# Global variables
faiss_index = None
metadata = None
legal_synonyms = {}

FAISS_INDEX_PATH = "data/faiss_index.bin"
METADATA_PATH = "data/metadata.pkl"
METADATA_PATH = "data/metadata.pkl"
SYNONYMS_PATH = "data/legal_synonyms.json"

def load_resources():
    """Load FAISS index, metadata, and synonyms"""
    global faiss_index, metadata, legal_synonyms
    
    # Load Synonym Map
    if os.path.exists(SYNONYMS_PATH):
        try:
            with open(SYNONYMS_PATH, 'r') as f:
                legal_synonyms = json.load(f)
            print(f"Loaded {len(legal_synonyms)} legal synonyms")
        except Exception as e:
            print(f"Error loading synonyms: {e}")
    else:
        print("Legal synonyms not found")

    # Load FAISS & Metadata
    try:
        if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
            faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            with open(METADATA_PATH, 'rb') as f:
                metadata = pickle.load(f)
            print(f"FAISS index loaded successfully with {faiss_index.ntotal} vectors")
        else:
            print("FAISS index not found. Please run ingest.py.")
            faiss_index = None
            metadata = None
    except Exception as e:
        print(f"Error loading FAISS index: {e}")
        faiss_index = None
        metadata = None

def create_embedding(text: str) -> np.ndarray:
    return embedding_model.encode([text])[0]

def detect_law_strict(query: str):
    """Detect Law from query for strict filtering"""
    q = query.lower()
    if "ipc" in q or "indian penal code" in q: return "IPC"
    if "crpc" in q or "criminal procedure" in q: return "CRPC"
    if "bns" in q or "nyaya sanhita" in q: return "BNS"
    if "bnss" in q or "nagarik suraksha" in q: return "BNSS"
    if "evidence" in q: return "EVIDENCE"
    if "constitution" in q: return "CONSTITUTION"
    return None

def detect_legal_intents(query: str) -> List[str]:
    """Detect multiple legal intents/sections from query"""
    q_lower = query.lower()
    found_sections = set()
    
    # 1. Direct Regex (e.g. "IPC 302")
    # Pattern B: "IPC 302"
    matches_b = re.findall(r'\b(ipc|crpc|bns|bnss)\s+(\d+[a-z]?)', q_lower)
    for law, sec in matches_b:
        found_sections.add(f"{law.upper()} {sec}")
        
    # Pattern C: "302 IPC"
    matches_c = re.findall(r'\b(\d+[a-z]?)\s+(ipc|crpc|bns|bnss)', q_lower)
    for sec, law in matches_c:
        found_sections.add(f"{law.upper()} {sec}")

    # 2. Synonym Mapping (Multi-Intent)
    for term, targets in legal_synonyms.items():
        if term in q_lower:
            # targets is now a LIST of strings, e.g. ["IPC 498A", "IPC 323"]
            if isinstance(targets, list):
                for t in targets:
                    found_sections.add(t)
            elif isinstance(targets, dict): # Old format fallback
                 if "keywords" in targets:
                     found_sections.add(targets['keywords']) # This might be loose text, but okay
            
    return list(found_sections)

def search_similar_documents(query: str, top_k: int = 12, use_rerank: bool = True) -> Dict:
    """Law-aware retrieval with Reranking, Intent Normalization, and Confidence Check"""
    if faiss_index is None or metadata is None:
        return {"type": "error", "documents": []}
    
    # 0. Intent Normalization is now handled in rag_pipeline
    # We proceed directly to strict or semantic search
    
    # 1. Detect Section and Law (Improved Regex)
    section_number = None
    law_tag_found = None
    
    # Pattern A: "Section 302"
    match_a = re.search(r'(?:section|article|order|rule)\s*(\d+[a-z]?)', query.lower())
    # Pattern B: "IPC 302" or "302 IPC" (Reverse)
    match_b = re.search(r'\b(ipc|crpc|bns|bnss)\s+(\d+[a-z]?)', query.lower())
    match_c = re.search(r'\b(\d+[a-z]?)\s+(ipc|crpc|bns|bnss)', query.lower())
    
    if match_a:
        section_number = match_a.group(1).lower()
    elif match_b:
        law_tag_found = match_b.group(1).upper()
        section_number = match_b.group(2).lower()
    elif match_c:
        section_number = match_c.group(1).lower()
        law_tag_found = match_c.group(2).upper()
        
    law_tag = detect_law_strict(query) or law_tag_found
    
    if section_number:
        if law_tag:
            # STRICT FILTER MODE (Law + Section)
            print(f"STRICT FILTER: Law={law_tag}, Section={section_number}")
            matches = [doc for doc in metadata if str(doc.get('section_number', '')).lower().strip() == section_number and doc.get('law') == law_tag]
            if matches:
                for m in matches: m['score'] = 1.0 
                return {"type": "strict_section", "documents": matches[:top_k]}
            else:
                 # If specific law asked (e.g. IPC 375) and NOT found, do not fall back to other laws.
                 # Trigger Web Search instead.
                 print(f"Specific Law {law_tag} Section {section_number} not found locally.")
                 return {"type": "low_confidence", "documents": []}
        
        # MULTI-LAW MODE (Section only)
        print(f"MULTI-LAW SECTION SEARCH: Section={section_number}")
        # Bias towards IPC if no law specified, but return all for clear comparison if needed
        # User requested "Prefer IPC (default)".
        matches = [doc for doc in metadata if str(doc.get('section_number', '')).lower().strip() == section_number]
        
        if matches:
            # Sort: IPC first, then others
            matches.sort(key=lambda x: 0 if x.get('law') == 'IPC' else 1)
            for m in matches: m['score'] = 0.9
            return {"type": "multi_section", "documents": matches[:top_k]}

    # 2. Normal Semantic Search with Reranking
    query_embedding = create_embedding(query).reshape(1, -1).astype('float32')
    candidate_k = max(top_k * 2, 20)
    distances, indices = faiss_index.search(query_embedding, candidate_k)
    
    semantic_candidates = []
    for idx, distance in zip(indices[0], distances[0]):
        if idx < len(metadata):
            doc = metadata[idx].copy()
            doc['score'] = float(distance)
            semantic_candidates.append(doc)
            
    if not semantic_candidates:
        return {"type": "error", "documents": []}

    # 3. Cross-Encoder Reranking
    if use_rerank:
        print(f"Reranking {len(semantic_candidates)} candidates...")
        pairs = [[query, doc['text']] for doc in semantic_candidates]
        rerank_scores = reranker.predict(pairs)
        
        for i, score in enumerate(rerank_scores):
            semantic_candidates[i]['rerank_score'] = float(score)
        
        # Sort by rerank score (descending)
        reranked_docs = sorted(semantic_candidates, key=lambda x: x['rerank_score'], reverse=True)
    else:
        # Fallback to simple distance sorting if no rerank
        reranked_docs = semantic_candidates
    
    # 4. Strict Relevance Threshold & Law Filtering
    query_law = detect_law_strict(query)
    
    # NEW: Legal Query Classification Routing
    # If not a specific section search (which is already strict), we use the classifier
    query_type = classify_legal_query(query)
    print(f"Query Classifier: '{query}' -> [{query_type}]")

    final_docs = []
    
    best_score = -99.0
    for doc in reranked_docs:
        score = doc.get('rerank_score', 0)
        if use_rerank and score > best_score:
            best_score = score
            
        # Relevance Gate: 
        # (REMOVED: rag_pipeline now handles confidence threshold)
        if False: # Keep structure for future logic if needed
             continue
             
        # Law Filter during strict law query
        if query_law and doc.get('law') and doc.get('law') != query_law:
            continue
            
        # Doc Type Filter (Routing)
        # If user asks for "Case law" or "Judgment", prioritize judgments
        if query_type == "judgment":
            if doc.get('doc_type') != 'judgment':
                 # Penalize or Skip? Skip is safer for accuracy.
                 continue

        # If user asks "Section", prioritize Statutes
        if query_type == "statute":
            if doc.get('doc_type') != 'statute':
                 continue
                 
        final_docs.append(doc)
        
    if not final_docs:
        print(f"⚠️ All docs rejected by Relevance Gate (Best Score: {best_score})")
        return {"type": "low_confidence", "documents": []}

    print(f"Retrieval Success: {len(final_docs)} docs found (Best Rerank Score: {best_score})")
    return {
        "type": "semantic",
        "documents": final_docs[:top_k]
    }

def perform_web_search(query: str) -> List[Dict]:
    """Fallback to Web Search using Tavily (Real Hybrid Search)"""
    if not TAVILY_AVAILABLE:
        return []
    
    print(f"Performing REAL Web Search for: {query}")
    try:
        search_query = f"Indian law {query} IPC section punishment explanation"
        
        results = tavily.search(
            query=search_query,
            search_depth="advanced",
            max_results=5
        )
        
        web_docs = []
        for r in results.get("results", []):
            web_docs.append({
                "title": r.get('title', 'Web Result'),
                "text": r.get('content', '')[:1000],  # Truncate per result
                "law": "Web Source",
                "section_number": "External",
                "score": 0.5,
                "source": r.get('url', 'Web')
            })
            
        return web_docs
        
    except Exception as e:
        print(f"Tavily Web Search failed: {e}")
        return []

def extract_legal_text(results: List[Dict]) -> str:
    """Extract and clean text from web results for LLM context"""
    combined = ""
    for r in results[:3]:
        combined += f"--- SOURCE: {r.get('title', 'Web')} ---\n{r.get('text', '')}\n\n"
    return combined[:2000]

def is_legal_query(query: str) -> bool:
    """Check if query contains at least one legal keyword"""
    q = query.lower()
    return any(word in q for word in LEGAL_KEYWORDS)

def generate_answer(query: str, retrieved_docs: List[Dict], source_label: str, mode: str = "research", chat_history: List[Dict] = None) -> str:
    """LexQuery Reasoning Engine: Decoupled Search vs. Chat Logic with Chat History support"""
    
    # 2. Tiered Context Strategy (Balance tokens vs quality)
    is_follow_up = (mode == "advice" and chat_history and len(chat_history) > 0)
    
    # Use more context for search, less for conversational follow-ups
    doc_limit = 1000 if mode == "research" else 500
    docs_to_use = retrieved_docs[:1] if is_follow_up else retrieved_docs[:3]
    
    context_items = []
    for d in docs_to_use:
        title = d.get('title', 'Unknown')
        law = d.get('law', 'Unknown')
        text = d.get('text', '')[:doc_limit]
        context_items.append(f"--- SOURCE: {title} ({law}) ---\n{text}")
    
    context_text = "\n\n".join(context_items)

    # 1. Backend Mode Selection & Message Structure
    model_name = "llama-3.1-8b-instant" # Consistent high-capacity model
    
    if mode == "research":
        system_prompt = SEARCH_PROMPT.replace("{source_label}", source_label)
        temperature = 0.0
        top_p = 0.1 
        max_tokens = 1024
        
        prompt = f"""
SYSTEM PROMPT:
{system_prompt}

LEGAL CONTEXT:
{context_text}

SOURCE LABEL:
{source_label}

USER QUERY:
{query}
"""
        messages = [{"role": "user", "content": prompt}]
    else:
        # Advice Mode (Chat)
        system_prompt = ASSISTANT_PROMPT.replace("{source_label}", source_label)
        temperature = 0.2
        top_p = 1.0 
        max_tokens = 220 
        
        messages = [
            {"role": "system", "content": f"{system_prompt}\n\nLEGAL CONTEXT:\n{context_text}"}
        ]
        
        # History: last 4 messages (2 pairs)
        if chat_history:
            messages.extend(chat_history[-4:])
        
        messages.append({"role": "user", "content": query})

    try:
        response = groq_client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR: Groq API failure ({model_name}): {error_msg}")
        
        if "rate_limit" in error_msg.lower():
            return "I am reaching temporary capacity limits. Please try again in 1 minute."
        return f"I encountered an error. (Detail: {error_msg[:40]}...)"

def rag_pipeline(query: str, top_k: int = 8, mode: str = "research", chat_history: List[Dict] = None) -> Dict:
    """Final Legal RAG Hierarchy: Local -> Confidence Gate -> Web"""
    try:
        # 1. Local Retrieval
        intents = detect_legal_intents(query)
        all_local_docs = []
        unique_doc_ids = set()
        
        if intents:
            for intent in intents:
                res = search_similar_documents(intent, top_k=3, use_rerank=True)
                if res.get('documents'):
                    for d in res['documents']:
                        doc_id = f"{d.get('law')}_{d.get('section_number')}"
                        if doc_id not in unique_doc_ids:
                            unique_doc_ids.add(doc_id)
                            all_local_docs.append(d)
        
        if not all_local_docs:
             res = search_similar_documents(query, top_k=top_k, use_rerank=True)
             if res.get('documents'):
                 all_local_docs = res['documents']
        
        # 2. Confidence Gate (Always using reranked score)
        best_score = -999.0
        if all_local_docs:
            # search_similar_documents already returns reranked docs if use_rerank=True
            best_score = all_local_docs[0].get('rerank_score', -999.0)

        threshold = 2.5 if mode == "advice" else -1.0
        is_low_confidence = (best_score < threshold)

        # 3. Decision Tree: Fallback or Local
        if is_low_confidence:
            print(f"Low Confidence ({best_score} < {threshold}). Triggering Web Fallback...")
            
            # Legal Gate
            # Always check legal gate if confidence is low, unless it's a very short follow-up
            # but even follow-ups shouldn't be about recipes.
            is_legal = is_legal_query(query)
            is_follow_up = (mode == "advice" and chat_history and len(chat_history) > 0)
            
            # If not legal keyword AND not a likely follow-up -> REJECT
            # We also reject if it looks like a recipe or general chat even if it's a "follow-up"
            if not is_legal:
                 # Check if it's a very short contextual follow-up (e.g. "where?", "how?")
                 if len(query.split()) > 3: # Longer non-legal queries are strictly rejected
                      return {
                        "answer": "I am a legal assistant and can only answer questions related to Indian Law. Please ask a legal question.",
                        "sources": [],
                        "query": query,
                        "type": "rejection"
                    }
                 
                 # If it's a follow-up but not about law, we let it pass to LLM ONLY if tiny
                 if not is_follow_up:
                      return {
                        "answer": "I am a legal assistant and can only answer questions related to Indian Law.",
                        "sources": [],
                        "query": query,
                        "type": "rejection"
                    }

            web_docs = perform_web_search(query)
            if web_docs:
                answer = generate_answer(query, web_docs, "External Legal Reference", mode, chat_history)
                return {
                    "answer": answer,
                    "sources": web_docs,
                    "query": query,
                    "type": "web_fallback"
                }
            else:
                 return {
                    "answer": "NO APPLICABLE LEGAL PROVISION FOUND IN DATABASE",
                    "sources": [],
                    "query": query,
                    "type": "error"
                 }
        
        # 4. Local High Confidence
        answer = generate_answer(query, all_local_docs[:3], "Database Legal Reference", mode, chat_history)
        return {
            "answer": answer,
            "sources": all_local_docs[:3],
            "query": query,
            "type": "local_authority"
        }

    except Exception as e:
        print(f"CRITICAL ERROR in rag_pipeline: {e}")
        return {
            "answer": f"An internal error occurred: {str(e)}",
            "sources": [],
            "query": query,
            "type": "error"
        }

# Load resources on import
load_resources()
