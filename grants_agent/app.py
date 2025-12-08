import streamlit as st
import json
import faiss
import numpy as np
import openai
from dotenv import load_dotenv
import os
import requests

# Load environment variables BEFORE any Streamlit commands
load_dotenv()

# THIS MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="USDA Grants Finder", layout="wide")

# Now load other configs
openai.api_key = os.getenv("OPENAI_API_KEY")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
EMBED_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o"

# Load FAISS index and metadata
FAISS_INDEX_PATH = "usda_grants.faiss"
META_PATH = "usda_grants_meta.json"

index = faiss.read_index(FAISS_INDEX_PATH)
with open(META_PATH, "r", encoding="utf-8") as f:
    programs = json.load(f)

# --- NEW: Match Score Calculator ---
def calculate_match_score(program, farmer_profile):
    """Calculate 0-100 match score based on farmer profile"""
    score = 50  # Base score
    
    if not farmer_profile:
        return score
    
    eligibility = " ".join(program.get("eligibility", [])).lower()
    
    # Boost for beginning farmers
    if farmer_profile.get("beginning_farmer") and "beginning" in eligibility:
        score += 30
    
    # Boost for veterans
    if farmer_profile.get("veteran") and "veteran" in eligibility:
        score += 20
    
    return min(score, 100)

# --- NEW: Simple Checklist Generator ---
def generate_simple_checklist(program):
    """Generate a simple application checklist"""
    
    checklist_text = f"""## Application Checklist for {program.get('program_name')}

### ✅ Before You Start
- [ ] Read full program details at: {program.get('official_url')}
- [ ] Check deadline: {program.get('application_deadlines')}
- [ ] Confirm you meet eligibility requirements

### 📋 Required Documents
"""
    
    for doc in program.get('required_documents', []):
        checklist_text += f"- [ ] {doc}\n"
    
    checklist_text += f"""
### 📞 Contact Information
If you have questions, contact: {program.get('contact_info')}

### 🚀 Next Steps
1. Gather all required documents
2. Contact your local office for guidance
3. Submit application via: {program.get('application_method')}

### 💡 Eligibility Requirements
"""
    
    for req in program.get('eligibility', []):
        checklist_text += f"- {req}\n"
    
    return checklist_text

# --- Web Search Function ---
def web_search_brave(query, num_results=5):
    """Search using Brave Search API"""
    if not BRAVE_API_KEY:
        st.error("⚠️ BRAVE_API_KEY not found in .env file!")
        return None
    
    url = "https://api.search.brave.com/res/v1/web/search"
    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": BRAVE_API_KEY
    }
    params = {
        "q": query,
        "count": num_results
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        web_results = data.get("web", {}).get("results", [])
        for item in web_results:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("description", ""),
                "link": item.get("url", "")
            })
        
        return results
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            st.error("🔑 Invalid Brave API key. Check your .env file.")
        elif e.response.status_code == 429:
            st.error("⏱️ Rate limit exceeded. You've used your monthly quota.")
        else:
            st.error(f"❌ Brave API error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Web search error: {str(e)}")
        return None

# --- Helper Functions ---
def embed_query(query):
    """Create embedding for query"""
    try:
        resp = openai.Embedding.create(model=EMBED_MODEL, input=query)
        return np.array(resp["data"][0]["embedding"]).astype("float32")
    except Exception as e:
        st.error(f"Embedding error: {str(e)}")
        return None

def search_local_programs(query, top_k=5, relevance_threshold=1.2):
    """Search local FAISS database with confidence scoring and match scores"""
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
            
            # NEW: Calculate match score
            program["_match_score"] = calculate_match_score(program, st.session_state.farmer_profile)
            
            results.append(program)
    
    # Sort by match score (highest first)
    results.sort(key=lambda x: x.get("_match_score", 0), reverse=True)
    
    avg_distance = float(np.mean(D[0])) if len(D[0]) > 0 else 999.0
    
    return results, avg_distance

def decide_search_strategy(query, local_results, avg_distance):
    """Decide whether to use local data, web search, or both"""
    query_lower = query.lower()
    
    web_indicators = [
        "latest", "recent", "new", "current", "2025", "2026",
        "updated", "changes", "announcement", "news"
    ]
    
    needs_web = any(indicator in query_lower for indicator in web_indicators)
    
    local_is_good = len(local_results) > 0 and avg_distance < 1.0
    local_is_moderate = len(local_results) > 0 and avg_distance < 1.5
    local_is_poor = avg_distance >= 1.5
    
    if local_is_poor:
        return "web_only"
    elif needs_web and local_is_moderate:
        return "hybrid"
    elif local_is_good and not needs_web:
        return "local_only"
    else:
        return "hybrid"

def generate_hybrid_response(query, local_results, web_results, strategy, conversation_history=None):
    """Generate response using local data, web data, or both"""
    # Build local context
    local_context = ""
    if local_results:
        local_parts = []
        for i, program in enumerate(local_results, 1):
            eligibility_str = ", ".join(program.get("eligibility", []))
            match_score = program.get("_match_score", 50)
            
            local_parts.append(f"""
Local Program {i}: {program.get("program_name", "N/A")}
- Match Score: {match_score}/100
- Match Confidence: {program.get("_confidence", 0):.2f}
- Type: {program.get("program_type", "N/A")}
- Agency: {program.get("agency", "N/A")}
- Eligibility: {eligibility_str}
- Funding: {program.get("funding_amount", "N/A")}
- Application Method: {program.get("application_method", "N/A")}
- Deadlines: {program.get("application_deadlines", "N/A")}
- URL: {program.get("official_url", "N/A")}
""")
        local_context = "\n---\n".join(local_parts)
    
    # Build web context
    web_context = ""
    if web_results:
        web_parts = []
        for i, result in enumerate(web_results, 1):
            web_parts.append(f"""
Web Result {i}: {result.get("title", "N/A")}
- Snippet: {result.get("snippet", "N/A")}
- Source: {result.get("link", "N/A")}
""")
        web_context = "\n---\n".join(web_parts)
    
    # Create system prompt based on strategy
    farmer_context = ""
    if st.session_state.farmer_profile:
        profile = st.session_state.farmer_profile
        farmer_context = f"""
**Farmer Profile:**
- Beginning Farmer: {profile.get('beginning_farmer', False)}
- Veteran: {profile.get('veteran', False)}
- State: {profile.get('state', 'Not specified')}

Use this profile to personalize your recommendations and highlight programs that are especially good matches.
"""
    
    if strategy == "web_only":
        system_prompt = f"""You are a USDA grants expert assistant. 

{farmer_context}

The user asked: "{query}"

I searched my local database of 8 USDA programs, but couldn't find relevant matches.

However, I found current information from the web:

**Web Search Results:**
{web_context}

**Instructions:**
- Answer based on the web results
- Cite sources with clickable links in markdown format: [Source Name](URL)
- Be clear that this info is from web search
- If web results don't fully answer the question, say so
- Suggest checking official USDA websites for complete details
- Be conversational and helpful"""

    elif strategy == "local_only":
        system_prompt = f"""You are a USDA grants expert with a database of 8 programs.

{farmer_context}

**Local Database Programs (sorted by match score):**
{local_context}

**Instructions:**
- Answer based on your local database
- Prioritize programs with higher match scores
- Be specific about which programs match the user's needs
- Include eligibility criteria and application details
- Provide official URLs from the programs
- Be conversational and helpful
- If asked about programs not in the database, say so clearly"""

    else:  # hybrid
        system_prompt = f"""You are a USDA grants expert with both a local database AND web search capabilities.

{farmer_context}

**Local Database Results (sorted by match score):**
{local_context}

**Web Search Results:**
{web_context}

**Instructions:**
- Combine information from both sources for a comprehensive answer
- Prioritize local programs with higher match scores
- Use local database for structured program details (eligibility, funding, deadlines)
- Use web results for updates, recent changes, or additional context
- Clearly distinguish between local database info and web sources
- Cite web sources with links: [Source](URL)
- Provide actionable next steps
- Be conversational and helpful"""

    messages = [{"role": "system", "content": system_prompt}]
    
    if conversation_history:
        for entry in conversation_history[-6:]:
            if entry["role"] in ["user", "assistant"]:
                content = entry["content"] if entry["role"] == "user" else entry.get("text", "")
                messages.append({
                    "role": entry["role"],
                    "content": content
                })
    
    messages.append({"role": "user", "content": query})
    
    try:
        response = openai.ChatCompletion.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.6,
            max_tokens=1200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# --- Streamlit UI ---

st.title("🌾 USDA Grants Finder")
st.write("Find and apply for USDA grants tailored to your farm")

# Check API keys
if not BRAVE_API_KEY:
    st.error("⚠️ BRAVE_API_KEY not found! Add it to your .env file.")
    st.info("Get a free API key at: https://brave.com/search/api/")
    st.stop()

if not openai.api_key:
    st.error("⚠️ OPENAI_API_KEY not found! Add it to your .env file.")
    st.stop()

st.success("✅ APIs configured: OpenAI + Brave Search")

# Session state
if "history" not in st.session_state:
    st.session_state.history = []

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# NEW: Farmer Profile in Session State
if "farmer_profile" not in st.session_state:
    st.session_state.farmer_profile = {}

# Layout
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("💬 Chat")
    
    # Display conversation
    for entry in st.session_state.history:
        if entry["role"] == "user":
            st.markdown(f"**You:** {entry['content']}")
        elif entry["role"] == "assistant":
            st.markdown(f"**Assistant:** {entry['text']}")
            
            strategy_badges = {
                "local_only": "📁 Local Database",
                "web_only": "🌐 Web Search",
                "hybrid": "🔄 Local + Web"
            }
            if entry.get("strategy"):
                st.caption(f"Source: {strategy_badges.get(entry['strategy'], 'Unknown')}")
            
            # NEW: Enhanced program display with match scores and checklists
            if entry.get("local_programs"):
                with st.expander(f"📁 Recommended Programs ({len(entry['local_programs'])})"):
                    for idx, prog in enumerate(entry["local_programs"]):
                        prog_name = prog.get("program_name", "Unknown")
                        confidence = prog.get("_confidence", 0)
                        match_score = prog.get("_match_score", 50)
                        
                        # Color code the match score
                        if match_score >= 70:
                            badge = "🟢 Great Match"
                            color = "green"
                        elif match_score >= 50:
                            badge = "🟡 Good Match"
                            color = "orange"
                        else:
                            badge = "🔴 Possible Match"
                            color = "red"
                        
                        st.markdown(f"### {badge}: {prog_name}")
                        st.markdown(f"**Match Score:** :{color}[{match_score}/100]")
                        st.markdown(f"**Search Relevance:** {confidence:.0%}")
                        st.markdown(f"**Funding:** {prog.get('funding_amount', 'N/A')}")
                        st.markdown(f"**Deadline:** {prog.get('application_deadlines', 'N/A')}")
                        st.markdown(f"**Type:** {prog.get('program_type', 'N/A')}")
                        
                        # NEW: Checklist button
                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"📝 Get Checklist", key=f"checklist_{idx}_{len(st.session_state.history)}"):
                                checklist = generate_simple_checklist(prog)
                                st.markdown(checklist)
                        
                        with col_b:
                            # Download checklist
                            checklist_data = generate_simple_checklist(prog)
                            st.download_button(
                                "⬇️ Download",
                                data=checklist_data,
                                file_name=f"{prog.get('program_id', 'program')}_checklist.md",
                                mime="text/markdown",
                                key=f"download_{idx}_{len(st.session_state.history)}"
                            )
                        
                        st.markdown("---")
            
            if entry.get("web_results"):
                with st.expander(f"🌐 Web Results ({len(entry['web_results'])})"):
                    for result in entry["web_results"]:
                        title = result.get("title", "No title")
                        link = result.get("link", "#")
                        snippet = result.get("snippet", "")
                        st.markdown(f"**[{title}]({link})**")
                        st.caption(snippet)
                        st.markdown("---")
    
    # Input
    user_input = st.text_input(
        "Ask about USDA programs:", 
        key="user_input", 
        placeholder="e.g., What grants are available for beginning farmers?"
    )
    
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        submit = st.button("Send", type="primary", use_container_width=True)
    with col_btn2:
        clear = st.button("Clear Chat", use_container_width=True)
    
    if clear:
        st.session_state.history = []
        st.rerun()
    
    if submit and user_input:
        st.session_state.pending_query = user_input

with col2:
    # NEW: Farmer Profile Section
    st.subheader("👨‍🌾 Your Profile")
    
    with st.form("farmer_profile_form"):
        st.write("Help us find the best grants for you:")
        
        is_beginning = st.checkbox(
            "Beginning Farmer (less than 10 years experience)",
            value=st.session_state.farmer_profile.get("beginning_farmer", False)
        )
        
        is_veteran = st.checkbox(
            "Veteran",
            value=st.session_state.farmer_profile.get("veteran", False)
        )
        
        state = st.text_input(
            "State",
            value=st.session_state.farmer_profile.get("state", ""),
            placeholder="e.g., Iowa"
        )
        
        save_profile = st.form_submit_button("💾 Save Profile", use_container_width=True)
        
        if save_profile:
            st.session_state.farmer_profile = {
                "beginning_farmer": is_beginning,
                "veteran": is_veteran,
                "state": state
            }
            st.success("✅ Profile saved!")
            st.rerun()
    
    # Show current profile
    if st.session_state.farmer_profile:
        st.info(f"""**Current Profile:**
- Beginning Farmer: {'Yes' if st.session_state.farmer_profile.get('beginning_farmer') else 'No'}
- Veteran: {'Yes' if st.session_state.farmer_profile.get('veteran') else 'No'}
- State: {st.session_state.farmer_profile.get('state', 'Not set')}
""")
    
    st.markdown("---")
    
    st.subheader("📚 Database Coverage")
    st.markdown("""
    **8 USDA Programs:**
    - Farm Operating Loans (FSA)
    - Farm Labor Housing (RHS)
    - Beginning Farmer Loans (FSA)
    - Crop/Livestock Insurance (RMA)
    - Marketing Grants (FSMIP, FMPP)
    - Specialty Crop Grants (SCBGP)
    - Organic Certification (FSA)
    """)
    
    st.markdown("---")
    st.subheader("💡 Quick Start")
    
    if st.button("🌱 Beginning farmer programs", use_container_width=True):
        st.session_state.pending_query = "What programs are available for beginning farmers?"
    
    if st.button("📅 Latest USDA grants 2025", use_container_width=True):
        st.session_state.pending_query = "What are the latest USDA grants for 2025?"
    
    if st.button("🌿 Organic certification help", use_container_width=True):
        st.session_state.pending_query = "How can I get help with organic certification costs?"
    
    st.markdown("---")
    st.caption("**API Usage:**")
    st.caption("• Brave: 2,000 searches/month")
    st.caption("• OpenAI: Pay per token")

# Footer
st.markdown("---")
st.caption("🔒 Your data is stored locally and never shared")

# Process pending query
if st.session_state.pending_query:
    query = st.session_state.pending_query
    st.session_state.pending_query = None
    
    st.session_state.history.append({"role": "user", "content": query})
    
    with st.spinner("🔍 Searching local database and web..."):
        # Step 1: Search local database
        local_results, avg_distance = search_local_programs(query, top_k=5)
        
        # Step 2: Decide strategy
        strategy = decide_search_strategy(query, local_results, avg_distance)
        
        # Step 3: Web search if needed
        web_results = None
        if strategy in ["web_only", "hybrid"]:
            search_query = f"USDA grants {query}"
            web_results = web_search_brave(search_query, num_results=5)
        
        # Step 4: Generate response
        response_text = generate_hybrid_response(
            query,
            local_results,
            web_results,
            strategy,
            st.session_state.history[:-1]
        )
        
        # Save to history
        st.session_state.history.append({
            "role": "assistant",
            "text": response_text,
            "local_programs": local_results,
            "web_results": web_results,
            "strategy": strategy
        })
    
    st.rerun()
