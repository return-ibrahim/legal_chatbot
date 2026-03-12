"""
Data Ingestion Script for LexQuery
This script loads legal documents, creates embeddings, and builds a FAISS index.
"""

import os
import pickle
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from typing import List, Dict

# Initialize embedding model
print("Loading BGE embedding model...")
_model = None

def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('BAAI/bge-base-en-v1.5')
    return _model

# Configuration
DATA_DIR = "data"
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.pkl")
SAMPLE_DATA_PATH = os.path.join(DATA_DIR, "legal_cases.csv")
CHUNK_SIZE = 500  # tokens


def create_sample_data():
    """Create sample legal dataset (replace with real data in production)"""
    sample_cases = [
        {
            "title": "State of Maharashtra v. Narayan Shamrao Puranik",
            "court": "Supreme Court of India",
            "date": "1985-03-15",
            "text": "This case deals with the interpretation of Section 302 IPC (Indian Penal Code) regarding murder. The Supreme Court held that the burden of proof lies on the prosecution to establish guilt beyond reasonable doubt. The court emphasized that circumstantial evidence must form a complete chain pointing to the guilt of the accused.",
            "source": "AIR 1985 SC 1"
        },
        {
            "title": "Kesavananda Bharati v. State of Kerala",
            "court": "Supreme Court of India",
            "date": "1973-04-24",
            "text": "This landmark judgment established the 'Basic Structure Doctrine' of the Indian Constitution. The Supreme Court ruled that while Parliament has the power to amend the Constitution, it cannot alter its basic structure. This includes principles like judicial review, separation of powers, and federalism.",
            "source": "AIR 1973 SC 1461"
        },
        {
            "title": "Vishaka v. State of Rajasthan",
            "court": "Supreme Court of India",
            "date": "1997-08-13",
            "text": "This case laid down guidelines for prevention of sexual harassment of women at workplace. The Court held that gender equality includes the right to work in an environment free from sexual harassment. These guidelines were later codified in the Sexual Harassment of Women at Workplace Act, 2013.",
            "source": "AIR 1997 SC 3011"
        },
        {
            "title": "Maneka Gandhi v. Union of India",
            "court": "Supreme Court of India",
            "date": "1978-01-25",
            "text": "This case expanded the scope of Article 21 (Right to Life and Personal Liberty). The Supreme Court held that 'life' does not merely mean animal existence but includes the right to live with human dignity. The procedure established by law must be just, fair, and reasonable.",
            "source": "AIR 1978 SC 597"
        },
        {
            "title": "Justice K.S. Puttaswamy (Retd.) vs Union Of India And Others",
            "court": "Supreme Court of India",
            "date": "2017-08-24",
            "text": "The Supreme Court in a historic judgment declared that the Right to Privacy is a fundamental right protected under Article 21 of the Constitution of India. The bench held that privacy is an intrinsic part of the right to life and personal liberty.",
            "source": "AIR 2017 SC 4161"
        },
        {
            "title": "Navtej Singh Johar vs Union of India",
            "court": "Supreme Court of India",
            "date": "2018-09-06",
            "text": "The Supreme Court decriminalized consensual homosexual sex between adults by reading down Section 377 of the IPC. The court held that discrimination on the basis of sexual orientation is a violation of the right to equality and privacy.",
            "source": "AIR 2018 SC 4321"
        },
        {
            "title": "M.C. Mehta v. Union of India (Oleum Gas Leak Case)",
            "court": "Supreme Court of India",
            "date": "1987-02-20",
            "text": "This case established the principle of 'Absolute Liability' for enterprises engaged in hazardous activities. The Court held that such enterprises must compensate for harm caused, regardless of fault. This ruling strengthened environmental protection and public safety standards in India.",
            "source": "AIR 1987 SC 1086"
        },
        {
            "title": "Indian Penal Code Section 420 - Cheating and dishonestly inducing delivery of property",
            "court": "Legislative Text",
            "date": "1860-01-01",
            "text": "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any person, or to make, alter or destroy the whole or any part of a valuable security, or anything which is signed or sealed, and which is capable of being converted into a valuable security, shall be punished with imprisonment of either description for a term which may extend to seven years, and shall also be liable to fine.",
            "source": "IPC Section 420"
        },
        {
            "title": "Code of Criminal Procedure Section 154 - Information in cognizable cases",
            "court": "Legislative Text",
            "date": "1973-01-01",
            "text": "Every information relating to the commission of a cognizable offence, if given orally to an officer in charge of a police station, shall be reduced to writing by him or under his direction, and be read over to the informant; and every such information, whether given in writing or reduced to writing as aforesaid, shall be signed by the person giving it, and the substance thereof shall be entered in a book to be kept by such officer.",
            "source": "CrPC Section 154"
        },
        {
            "title": "Indian Contract Act Section 10 - What agreements are contracts",
            "court": "Legislative Text",
            "date": "1872-01-01",
            "text": "All agreements are contracts if they are made by the free consent of parties competent to contract, for a lawful consideration and with a lawful object, and are not hereby expressly declared to be void. Essential elements of a valid contract include offer, acceptance, consideration, legal capacity, lawful object, and free consent.",
            "source": "Contract Act Section 10"
        }
    ]
    
    df = pd.DataFrame(sample_cases)
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(SAMPLE_DATA_PATH, index=False)
    print(f"✅ Sample data created with {len(sample_cases)} legal cases")
    return df


def chunk_text(text: str, max_tokens: int = CHUNK_SIZE) -> List[str]:
    """Split text into chunks (simple word-based chunking)"""
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_tokens):
        chunk = " ".join(words[i:i + max_tokens])
        chunks.append(chunk)
    
    return chunks if chunks else [text]


import pypdf

import re

def detect_law_from_metadata(filename: str, content_snippet: str = ""):
    """Normalize law name from filename or content for structured filtering"""
    name = filename.lower().replace("_", " ").replace("-", " ")
    snippet = content_snippet.lower()
    
    # 1. Check Filename
    if "penal" in name or "ipc" in name:
        return "IPC"
    if "nyaya sanhita" in name or "bns" in name:
        return "BNS"
    if "nagarik suraksha" in name or "bnss" in name:
        return "BNSS"
    if "criminal procedure" in name or "crpc" in name:
        return "CRPC"
    if "evidence" in name:
        return "EVIDENCE"
    if "constitution" in name:
        return "CONSTITUTION"
    
    # 2. Check Content Snippet (Fallback for generic names like 'repealed.pdf')
    if "indian penal code" in snippet:
        return "IPC"
    if "bharatiya nyaya sanhita" in snippet:
        return "BNS"
    if "code of criminal procedure" in snippet:
        return "CRPC"
    if "constitution of india" in snippet:
        return "CONSTITUTION"
        
    return "UNKNOWN"


def split_into_sections(text: str) -> List[Dict]:
    """
    Split text into sections using adaptive regex for different Bare Act formats.
    """
    sections = []
    
    # Strategy 1: "Section 302" or "Article 21" at start of line
    pattern1 = r'(?m)^\s*(Section|Article)\s+(\d+[A-Z]?\.?)(.*?)(?=(?:^\s*(?:Section|Article)\s+\d+[A-Z]?\.?)|$)'
    matches1 = list(re.finditer(pattern1, text, re.DOTALL | re.IGNORECASE))
    
    # Strategy 2: "302." or "1." at start of line
    pattern2 = r'(?m)^\s*(\d+[A-Z]?)\s*\.\s*(.*?)(?=(?:^\s*\d+[A-Z]?\s*\.)|$)'
    matches2 = list(re.finditer(pattern2, text, re.DOTALL))
    
    # Decide which strategy to use based on match count
    if len(matches1) > len(matches2):
        for m in matches1:
            h_type, sec_num, content = m.group(1), m.group(2), m.group(3)
            if len(content.strip()) < 60: continue
            
            title_match = re.search(r'^[.\s—]*(.+?)(?:\.|$)', content.strip(), re.MULTILINE)
            title = title_match.group(1).strip() if title_match else f"{h_type} {sec_num}"
            
            sections.append({
                "text": f"{h_type} {sec_num} {content.strip()}",
                "section_number": sec_num.strip('.'),
                "title": title[:100]
            })
    else:
        for m in matches2:
            sec_num, content = m.group(1), m.group(2)
            if len(content.strip()) < 60: continue
            
            title_match = re.search(r'^[^a-zA-Z]*(.+?)(?:\.|$)', content.strip(), re.MULTILINE)
            title = title_match.group(1).strip() if title_match else f"Section {sec_num}"
            
            sections.append({
                "text": f"Section {sec_num} {content.strip()}",
                "section_number": sec_num.strip('.'),
                "title": title[:100]
            })

    return sections


def load_and_process_data(csv_path: str) -> tuple:
    """Load CSV and PDF data and create chunks with metadata"""
    all_chunks = []
    metadata = []
    
    # helper to detect law from arbitrary text
    def quick_detect_law(t: str):
        t = t.lower()
        if "ipc" in t or "penal code" in t: return "IPC"
        if "crpc" in t or "criminal procedure" in t: return "CRPC"
        if "bns" in t or "nyaya sanhita" in t: return "BNS"
        if "bnss" in t or "suraksha sanhita" in t: return "BNSS"
        if "contract" in t: return "CONTRACT_ACT"
        if "constitution" in t or "article" in t: return "CONSTITUTION"
        return "PREVIOUS_JUDGMENT"
    
    def quick_extract_sec(t: str):
        m = re.search(r'(?:Section|Article)\s+(\d+[A-Z]?)', t, re.IGNORECASE)
        return m.group(1) if m else "General"

    def determine_doc_type(title: str, source: str, law: str) -> str:
        """Determine if document is Statute, Judgment, or Concept"""
        start_lower = title.lower()
        if "v." in start_lower or "vs" in start_lower or "union of india" in start_lower:
            return "judgment"
        if "section" in start_lower or "article" in start_lower or law in ["IPC", "CRPC", "BNS", "BNSS", "CONSTITUTION"]:
             # If it looks like a case title even with section, prioritize judgment
             if "v." in start_lower: return "judgment"
             return "statute"
        return "law_concept"

    # 1. Load CSV Data
    if os.path.exists(csv_path):
        print(f"Loading CSV data from {csv_path}...")
        df = pd.read_csv(csv_path)
        for _, row in df.iterrows():
            text = str(row['text'])
            title = str(row['title'])
            source = str(row['source'])
            
            # Detect Law and Section from CSV fields
            law = quick_detect_law(title + " " + source)
            sec = quick_extract_sec(title + " " + source)
            d_type = determine_doc_type(title, source, law)
            
            all_chunks.append(text)
            metadata.append({
                'title': row['title'],
                'court': row.get('court', 'Unknown'),
                'date': str(row.get('date', 'Unknown')),
                'source': source,
                'law': law,
                'doc_type': d_type,
                'section_number': sec, 
                'text': text
            })
    
    # 2. Load PDF Data
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.pdf')]
    print(f"Found {len(pdf_files)} PDF documents in {DATA_DIR}")
    
    for pdf_file in pdf_files:
        pdf_path = os.path.join(DATA_DIR, pdf_file)
        try:
            print(f"Processing {pdf_file}...")
            reader = pypdf.PdfReader(pdf_path)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
            
            # Use Section-Aware Splitting logic
            law_tag = detect_law_from_metadata(pdf_file, full_text[:2000])
            sections = split_into_sections(full_text)
            
            print(f"  -> Extracted {len(sections)} sections from {pdf_file} [Law: {law_tag}]")
            
            for section in sections:
                all_chunks.append(section['text'])
                metadata.append({
                    'title': section['title'],
                    'court': "Indian Law Document",
                    'date': "2023-2024",
                    'source': pdf_file,
                    'law': law_tag,
                    'doc_type': "statute", # Bare Acts are always statutes
                    'section_number': section['section_number'],
                    'text': section['text']
                })
                
        except Exception as e:
            print(f"❌ Error reading {pdf_file}: {e}")

    if not all_chunks:
        print("⚠️  No data found in CSV or PDFs. Creating sample data...")
        df = create_sample_data()
        for _, row in df.iterrows():
            text = str(row['text'])
            chunks = chunk_text(text)
            for chunk in chunks:
                all_chunks.append(chunk)
                metadata.append({
                    'title': row['title'],
                    'court': row['court'],
                    'date': row['date'],
                    'source': row['source'],
                    'section': "Unknown",
                    'doc_type': "concept" if "Legislative" not in row['court'] else "statute",
                    'text': chunk
                })

    print(f"✅ Processed total {len(all_chunks)} chunks from {len(pdf_files)} PDFs and CSV")
    return all_chunks, metadata



def create_embeddings(texts: List[str]) -> np.ndarray:
    """Create embeddings for all text chunks in batches"""
    print(f"Creating embeddings for {len(texts)} chunks...")
    
    batch_size = 32
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        try:
            # print(f"  Processing batch {i} to {i+len(batch)}...")
            embeddings = embedding_model.encode(batch, show_progress_bar=False)
            all_embeddings.append(embeddings)
        except Exception as e:
            print(f"❌ Error creating embeddings for batch starting at {i}: {e}")
            # Append zero embeddings or skip? 
            # Skipping messes up index alignment with metadata. 
            # Better to append zeros or try individually?
            # For now, let's just re-raise to fail fast, but maybe the batch size reduction fixes it.
            raise e
            
    if not all_embeddings:
        return np.array([]).astype('float32')
        
    return np.vstack(all_embeddings).astype('float32')


def build_faiss_index(embeddings: np.ndarray) -> faiss.Index:
    """Build FAISS index for efficient similarity search"""
    dimension = embeddings.shape[1]
    
    # Use IndexFlatL2 for exact search (good for small-medium datasets)
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    
    print(f"✅ FAISS index created with {index.ntotal} vectors (dimension: {dimension})")
    return index


def save_index_and_metadata(index: faiss.Index, metadata: List[Dict]):
    """Save FAISS index and metadata to disk"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Save FAISS index
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"✅ FAISS index saved to {FAISS_INDEX_PATH}")
    
    # Save metadata
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump(metadata, f)
    print(f"✅ Metadata saved to {METADATA_PATH}")


def main():
    """Main ingestion pipeline"""
    print("=" * 60)
    print("LexQuery Data Ingestion Pipeline")
    print("=" * 60)
    
    # Step 0: Ensure sample data exists
    create_sample_data()
    
    # Step 1: Load and process data
    chunks, metadata = load_and_process_data(SAMPLE_DATA_PATH)
    
    # Debug info
    print(f"DEBUG: Collected {len(chunks)} chunks.")
    if chunks:
        print(f"DEBUG: Avg chunk length: {sum(len(c) for c in chunks)/len(chunks):.0f} characters")
        print(f"DEBUG: Max chunk length: {max(len(c) for c in chunks)} characters")
    
    # Step 2: Create embeddings
    embeddings = create_embeddings(chunks)
    
    # Step 3: Build FAISS index
    index = build_faiss_index(embeddings)
    
    # Step 4: Save everything
    save_index_and_metadata(index, metadata)
    
    print("\n" + "=" * 60)
    print("✅ Data ingestion completed successfully!")
    print(f"📊 Total documents: {len(set(m['title'] for m in metadata))}")
    print(f"📦 Total chunks: {len(chunks)}")
    if len(embeddings) > 0:
        print(f"🔢 Vector dimension: {embeddings.shape[1]}")
    print("=" * 60)


if __name__ == "__main__":
    main()
