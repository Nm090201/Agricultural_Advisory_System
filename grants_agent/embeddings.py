from openai import OpenAI
import numpy as np
import faiss
import json
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Model configuration
EMBED_MODEL = "text-embedding-3-large"
FAISS_INDEX_PATH = "data/usda_grants.faiss"
META_PATH = "data/usda_grants_meta.json"

# Load once at module level
index = faiss.read_index(FAISS_INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    programs = json.load(f)

def embed_query(query):
    """Create embedding for query using OpenAI 1.0+ syntax"""
    try:
        response = client.embeddings.create(
            model=EMBED_MODEL,
            input=query
        )
        return np.array(response.data[0].embedding).astype("float32")
    except Exception as e:
        raise Exception(f"Embedding error: {str(e)}")

def search_local_programs(query, farmer_profile, top_k=5, relevance_threshold=1.2):
    """Search local FAISS database"""
    from agents.grant_finder import calculate_match_score
    
    q_emb = embed_query(query)
    if q_emb is None:
        return [], 999
    
    D, I = index.search(np.array([q_emb]), top_k)
    
    results = []
    for idx, distance in zip(I[0], D[0]):
        if distance < relevance_threshold:
            program = programs[idx].copy()
            program["_distance"] = float(distance)
            program["_confidence"] = 1 / (1 + distance)
            program["_match_score"] = calculate_match_score(program, farmer_profile)
            results.append(program)
    
    # Sort by match score
    results.sort(key=lambda x: x.get("_match_score", 0), reverse=True)
    
    avg_distance = float(np.mean(D[0])) if len(D[0]) > 0 else 999.0
    return results, avg_distance