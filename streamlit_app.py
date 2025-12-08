import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import json
import time
from dotenv import load_dotenv
import os

# Load environment variables FIRST
load_dotenv()

# Verify API key is loaded
if not os.getenv("OPENAI_API_KEY"):
    st.error("⚠️ OPENAI_API_KEY not found in .env file!")
    st.stop()

# Configuration
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="🌾 Agricultural Advisory System",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': "# 🌾 Agricultural Advisory System\n"
                "Helping farmers make better decisions with AI-powered insights.\n\n"
                "Analyze your soil, check market prices, and find grants - all in one place!"
    }
)

# Custom CSS - Agricultural Theme with Light Background, Larger Text, Clean Interface
st.markdown("""
    <style>
    /* Agricultural Color Palette */
    :root {
        --farm-green: #2E7D32;
        --crop-yellow: #F9A825;
        --soil-brown: #6D4C41;
        --sky-blue: #1976D2;
        --wheat-gold: #FBC02D;
        --earth-tan: #A1887F;
        --light-beige: #F5F5DC;
        --cream: #FFFEF7;
    }
    
    /* Main app background - Light Beige */
    .stApp {
        background-color: #F5F5DC;
        color: #000000;
        font-size: 1.1rem;
        font-weight: 500;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #FFFEF7;
        padding: 3rem;
        border-radius: 12px;
        max-width: 1400px;
    }
    
    /* All text black, bigger and bolder */
    .stMarkdown, .stText, p, span, div, label, li {
        color: #000000 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        line-height: 1.5 !important;
    }
    
    /* Reduce paragraph spacing */
    p {
        margin-bottom: 0.5rem !important;
    }
    
    /* Bullet points - tighter spacing */
    ul li, ol li {
        color: #000000 !important;
        font-size: 1.1rem !important;
        margin: 0.3rem 0 !important;
        line-height: 1.4 !important;
    }
    
    ul, ol {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Links should be blue but still readable */
    a {
        color: #1976D2 !important;
        font-weight: 600 !important;
        text-decoration: underline;
    }
    
    a:hover {
        color: #0D47A1 !important;
    }
    
    /* Stronger emphasis for bold text */
    strong, b {
        font-weight: 700 !important;
        font-size: 1.15rem !important;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 3.5rem !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #2E7D32 0%, #66BB6A 50%, #FBC02D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 1rem;
        font-family: 'Georgia', serif;
        letter-spacing: 1px;
    }
    
    .sub-header {
        text-align: center;
        color: #6D4C41 !important;
        margin-bottom: 1.5rem !important;
        font-size: 1.4rem !important;
        font-style: italic;
        font-family: 'Georgia', serif;
        font-weight: 500 !important;
    }
    
    /* Step headers - bigger and cleaner but tighter spacing */
    .step-header {
        background: linear-gradient(135deg, #6D4C41 0%, #8D6E63 50%, #A1887F 100%);
        color: white !important;
        padding: 1.5rem 2rem;
        border-radius: 15px;
        margin: 1.5rem 0 1rem 0 !important;
        font-weight: 700 !important;
        font-size: 1.8rem !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        border-left: 8px solid #FBC02D;
        letter-spacing: 0.5px;
    }
    
    /* Completed step styling */
    .completed-step {
        background: linear-gradient(135deg, #2E7D32 0%, #43A047 50%, #66BB6A 100%);
        opacity: 0.95;
    }
    
    /* Progress bar - thicker */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #2E7D32 0%, #66BB6A 50%, #FBC02D 100%);
        height: 12px;
    }
    
    /* Buttons - bigger and cleaner */
    .stButton>button {
        background: linear-gradient(135deg, #2E7D32 0%, #43A047 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        transition: all 0.3s !important;
        letter-spacing: 0.5px !important;
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Download buttons - ensure visibility */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #1976D2 0%, #1565C0 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2) !important;
        transition: all 0.3s !important;
    }
    
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #0D47A1 0%, #1565C0 100%) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.3) !important;
        transform: translateY(-3px) !important;
    }
    
    /* Form submit buttons - highly visible */
    .stFormSubmitButton>button {
        background: linear-gradient(135deg, #2E7D32 0%, #43A047 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 1.2rem 2.5rem !important;
        font-weight: 700 !important;
        font-size: 1.3rem !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.25) !important;
        transition: all 0.3s !important;
        letter-spacing: 1px !important;
    }
    
    .stFormSubmitButton>button:hover {
        background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 100%) !important;
        box-shadow: 0 8px 16px rgba(0,0,0,0.35) !important;
        transform: translateY(-4px) !important;
    }
    
    /* Secondary buttons (for different actions) */
    .stButton>button[kind="secondary"] {
        background: linear-gradient(135deg, #FBC02D 0%, #F9A825 100%) !important;
        color: #000000 !important;
    }
    
    .stButton>button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #F9A825 0%, #F57F17 100%) !important;
    }
    
    /* Sidebar styling - Light Beige with compact spacing */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F5F5DC 0%, #FFFEF7 100%);
        border-right: 4px solid #6D4C41;
        padding: 1.5rem 1rem;
    }
    
    [data-testid="stSidebar"] * {
        color: #000000 !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin: 0.8rem 0 0.5rem 0 !important;
    }
    
    [data-testid="stSidebar"] .element-container {
        margin: 0.3rem 0 !important;
    }
    
    /* Metric cards - bigger */
    [data-testid="stMetricValue"] {
        color: #2E7D32 !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #000000 !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    
    /* Success/Info/Warning boxes - cleaner with less space */
    .element-container div[data-baseweb="notification"] {
        border-left: 6px solid #2E7D32;
        background-color: #E8F5E9;
        color: #000000 !important;
        padding: 1rem !important;
        border-radius: 10px;
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Expander headers - bigger */
    .streamlit-expanderHeader {
        background-color: #F5F5DC;
        border-radius: 10px;
        border-left: 6px solid #6D4C41;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        color: #000000 !important;
        padding: 1rem 1.5rem;
    }
    
    /* Info boxes - less padding */
    .stAlert {
        border-radius: 10px;
        border-left: 6px solid #FBC02D;
        background-color: #FFFEF7;
        color: #000000 !important;
        padding: 1rem !important;
        font-size: 1.15rem !important;
        font-weight: 500 !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Input fields - bigger and cleaner */
    .stTextInput input, .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 3px solid #6D4C41 !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    
    /* Selectbox styling - make it look like text input */
    .stSelectbox > div > div {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 3px solid #6D4C41 !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    
    /* Selectbox dropdown arrow */
    .stSelectbox svg {
        fill: #000000 !important;
    }
    
    /* Selectbox options */
    [data-baseweb="popover"] {
        background-color: #FFFFFF !important;
        border: 3px solid #6D4C41 !important;
        border-radius: 10px !important;
    }
    
    [role="option"] {
        color: #000000 !important;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
        padding: 0.8rem 1rem !important;
    }
    
    [role="option"]:hover {
        background-color: #E8F5E9 !important;
    }
    
    .stTextInput label, .stNumberInput label, .stSelectbox label {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
        margin-bottom: 0.5rem;
    }
    
    /* Radio buttons and checkboxes - bigger */
    .stRadio label, .stCheckbox label {
        color: #000000 !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }
    
    /* Dataframes and tables - cleaner */
    .stDataFrame, .stTable {
        background-color: #FFFFFF;
        color: #000000 !important;
        font-size: 1.1rem !important;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .stDataFrame th {
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        background-color: #2E7D32;
        color: white !important;
        padding: 1rem;
    }
    
    .stDataFrame td {
        padding: 0.8rem;
        font-size: 1.1rem !important;
        font-weight: 500 !important;
    }
    
    /* Headers in content - bigger and bolder but tighter spacing */
    h1 {
        color: #2E7D32 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        margin: 1.5rem 0 0.8rem 0 !important;
        letter-spacing: 0.5px;
    }
    
    h2 {
        color: #2E7D32 !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 1.2rem 0 0.6rem 0 !important;
    }
    
    h3 {
        color: #2E7D32 !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    
    h4 {
        color: #6D4C41 !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
        margin: 0.8rem 0 0.4rem 0 !important;
    }
    
    /* Captions - slightly bigger */
    .caption, [data-testid="stCaptionContainer"] {
        color: #6D4C41 !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    /* Cleaner spacing */
    .element-container {
        margin: 1rem 0;
    }
    
    /* Remove wheat emoji decorations for cleaner look */
    h1::before, h2::before, h3::before {
        content: "";
    }
    
    /* Columns - more space between */
    [data-testid="column"] {
        padding: 0 1rem;
    }
    
    /* Form styling - cleaner */
    [data-testid="stForm"] {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        border: 3px solid #6D4C41;
        margin: 1rem 0;
    }
    
    /* Cleaner dividers */
    hr {
        border: none;
        border-top: 3px solid #6D4C41;
        margin: 2rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_step' not in st.session_state:
    st.session_state.workflow_step = 1
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = {}
if 'soil_result' not in st.session_state:
    st.session_state.soil_result = None
if 'market_results' not in st.session_state:
    st.session_state.market_results = {}
if 'recommended_crops' not in st.session_state:
    st.session_state.recommended_crops = []
if 'grant_results' not in st.session_state:
    st.session_state.grant_results = []

# Header
st.markdown('<p class="main-header">🌾 Agricultural Advisory System 🚜</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Empowering Farmers with AI-Driven Insights for Better Harvests</p>', unsafe_allow_html=True)

# Sidebar - Streamlined UI
with st.sidebar:
    st.markdown("### 🌾 Your Farming Journey")
    
    progress = (st.session_state.workflow_step - 1) * 25
    st.progress(progress / 100)
    st.caption(f"Step {st.session_state.workflow_step} of 5")

    # Step list (compact rendering)
    steps = [
        ("👨‍🌾", "Farm Profile"),
        ("🌍", "Soil & Climate"),
        ("📈", "Market Insights"),
        ("📋", "Action Plan")
    ]

    for idx, (emoji, name) in enumerate(steps, start=1):
        if st.session_state.workflow_step > idx:
            st.markdown(f"**{emoji} {name}**")
        elif st.session_state.workflow_step == idx:
            st.markdown(f"**{emoji} {name}**")
        else:
            st.markdown(f"{emoji} {name}")

    st.markdown("---")

    # API status (cleaner logic)
    st.markdown("#### 🔧 System Status")
    try:
        ok = requests.get(f"{API_URL}/", timeout=5).status_code == 200
        st.success("🟢 Online" if ok else "🔴 Error")
    except:
        st.error("🔴 Offline")
        st.caption("Start backend server")

    # How it works (more concise)
    with st.expander("ℹ️ How This Works"):
        st.markdown("""
        1️⃣ Share farm details  
        2️⃣ Soil + climate analysis  
        3️⃣ Market insights  
        4️⃣ Grant matching  
        5️⃣ Full action plan  
        """)

    st.markdown("---")

    if st.button("🔄 Start New Analysis", use_container_width=True):
        st.session_state.clear()
        st.session_state.workflow_step = 1
        st.session_state.customer_data = {}
        st.rerun()

# ============================================
# STEP 1: FARM PROFILE
# ============================================
if st.session_state.workflow_step == 1:
    st.markdown('<div class="step-header">🌱 Step 1: Tell Us About Your Farm</div>', unsafe_allow_html=True)
    st.markdown("*We need just a few details to give you the best farming advice tailored to your land and goals.*")
    
    with st.form("profile_form"):
        # Simplified to only 5 essential inputs
        st.markdown("### 📝 Essential Information")
        st.caption("*Just 5 quick questions to get started*")
        
        # Location
        st.markdown("#### 📍 Location")
        location_type = st.radio(
            "How would you like to specify your location?",
            ["Location Name", "GPS Coordinates"],
            horizontal=True
        )
        
        if location_type == "Location Name":
            location_name = st.text_input(
                "Enter your location *",
                placeholder="e.g., Ames, Iowa or Punjab, India",
                help="Enter your city, region, or nearest town"
            )
            latitude = None
            longitude = None
        else:
            col_a, col_b = st.columns(2)
            with col_a:
                latitude = st.number_input("Latitude *", value=42.0308, format="%.4f")
            with col_b:
                longitude = st.number_input("Longitude *", value=-93.6319, format="%.4f")
            location_name = None
        
        # Quick location buttons
        st.caption("Quick Select:")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            quick_iowa = st.form_submit_button("🌾 Iowa, USA", use_container_width=True)
        with col2:
            quick_punjab = st.form_submit_button("🌾 New York, USA", use_container_width=True)
        with col3:
            quick_brazil = st.form_submit_button("🌾 Texas, USA", use_container_width=True)
        with col4:
            quick_australia = st.form_submit_button("🌾 Chicago, USA", use_container_width=True)
        
        st.markdown("---")
        
        # Create 2 columns for the 4 remaining inputs
        col1, col2 = st.columns(2)
        
        with col1:
            # Farm Size
            st.markdown("#### 🚜 Farm Size")
            farm_size = st.number_input(
                "Total farm area (acres) *",
                min_value=1,
                max_value=100000,
                value=100,
                help="Enter the total cultivable area of your farm"
            )
            
            # Experience Level
            st.markdown("#### 👨‍🌾 Experience Level")
            experience = st.select_slider(
                "Your farming experience *",
                options=["Beginner", "Intermediate", "Experienced", "Expert"],
                value="Intermediate",
                help="Select your level of farming experience"
            )
        
        with col2:
            # Risk Tolerance
            st.markdown("#### 🎲 Risk Tolerance")
            risk_tolerance = st.select_slider(
                "How much risk are you willing to take? *",
                options=["Very Low", "Low", "Medium", "High", "Very High"],
                value="Medium",
                help="Very Low = Safe, proven crops | Very High = Higher risk, potentially higher returns"
            )
            
            # Budget
            st.markdown("#### 💰 Investment Budget")
            budget = st.selectbox(
                "Available budget for this season *",
                ["< $5,000", "$5,000 - $20,000", "$20,000 - $50,000", "> $50,000"],
                help="Select your investment capacity for seeds, inputs, and labor"
            )
        
        # Submit
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submit_profile = st.form_submit_button(
                "✅ Start Analysis",
                use_container_width=True,
                type="primary"
            )
        
        if submit_profile or quick_iowa or quick_punjab or quick_brazil or quick_australia:
            # Handle quick selections
            if quick_iowa:
                location_name = "Iowa, USA"
            elif quick_punjab:
                location_name = "New York, USA"
            elif quick_brazil:
                location_name = "Texas, USA"
            elif quick_australia:
                location_name = "Chicago, USA"
            
            # Validate
            if not location_name and (latitude is None or longitude is None):
                st.error("❌ Please provide location information")
            elif farm_size <= 0:
                st.error("❌ Please provide valid farm size")
            else:
                # Save only the 5 essential inputs
                st.session_state.customer_data = {
                    'location_name': location_name,
                    'latitude': latitude,
                    'longitude': longitude,
                    'farm_size': farm_size,
                    'experience': experience,
                    'risk_tolerance': risk_tolerance,
                    'budget': budget
                }
                
                st.session_state.workflow_step = 2
                st.success("✅ Profile saved! Moving to Soil & Climate Analysis...")
                time.sleep(1)
                st.rerun()

# ============================================
# STEP 2: SOIL & CLIMATE ANALYSIS
# ============================================
elif st.session_state.workflow_step == 2:
    st.markdown('<div class="step-header">🌍 Step 2: Soil & Climate Analysis for Your Farm</div>', unsafe_allow_html=True)
    
    # Show profile summary
    data = st.session_state.customer_data
    
    with st.expander("📋 Your Profile Summary", expanded=False):
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📍 Location", data.get('location_name', 'GPS'))
        with col2:
            st.metric("🚜 Farm Size", f"{data.get('farm_size')} acres")
        with col3:
            st.metric("👨‍🌾 Experience", data.get('experience', 'N/A'))
        with col4:
            st.metric("🎲 Risk", data.get('risk_tolerance', 'N/A'))
        with col5:
            st.metric("💰 Budget", data.get('budget', 'N/A'))
    
    st.markdown("---")
    
    # Auto-run analysis or manual trigger
    if st.session_state.soil_result is None:
        st.info("🌾 We'll analyze your land's soil and climate to recommend the best crops for your farm.")
        
        if st.button("🚀 Analyze My Farm's Conditions", type="primary", use_container_width=True):
            with st.spinner("🤖 Agent 1 is analyzing environmental data..."):
                try:
                    # Prepare payload
                    payload = {}
                    if data.get('location_name'):
                        payload["location_name"] = data['location_name']
                    else:
                        payload["latitude"] = data['latitude']
                        payload["longitude"] = data['longitude']
                    
                    # Call API
                    response = requests.post(
                        f"{API_URL}/recommend",
                        json=payload,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        st.session_state.soil_result = response.json()
                        
                        # Extract crop names
                        recs = st.session_state.soil_result.get('recommendations', [])
                        if isinstance(recs, list):
                            st.session_state.recommended_crops = [
                                rec.get('crop', '') for rec in recs if rec.get('crop')
                            ]
                        
                        st.success("✅ Analysis Complete!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display results if available
    if st.session_state.soil_result:
        result = st.session_state.soil_result
        
        st.success("✅ Soil & Climate Analysis Complete!")
        
        # Environmental summary
        st.markdown("### 🌍 Environmental Conditions")
        env = result.get("environmental_summary", {})
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌡️ Temperature", f"{env.get('temperature', 'N/A')}°C")
        with col2:
            st.metric("🏞️ Soil Type", env.get('soil_type', 'Unknown'))
        with col3:
            soil_tex = env.get('soil_texture', {})
            st.metric("🪨 Clay", f"{soil_tex.get('clay', 0):.1f}%")
        with col4:
            st.metric("🏖️ Sand", f"{soil_tex.get('sand', 0):.1f}%")
        
        # Crop Recommendations
        st.markdown("---")
        st.markdown("### 🌱 Recommended Crops for Your Farm")
        
        recs = result.get("recommendations", [])
        if isinstance(recs, list) and len(recs) > 0:
            for idx, rec in enumerate(recs, 1):
                crop_name = rec.get('crop', f'Crop {idx}')
                
                with st.expander(f"**#{idx}: {crop_name}**", expanded=(idx == 1)):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.success(f"**✅ Why it fits:** {rec.get('reason', 'Well-suited')}")
                    with col2:
                        st.warning(f"**⚠️ Risk:** {rec.get('risk', 'Standard risks')}")
        
        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Back to Profile", use_container_width=True):
                st.session_state.workflow_step = 1
                st.rerun()
        
        with col3:
            if st.button("➡️ Analyze Markets", type="primary", use_container_width=True):
                st.session_state.workflow_step = 3
                st.rerun()

# ============================================
# STEP 3: MARKET ANALYSIS
# ============================================
elif st.session_state.workflow_step == 3:
    st.markdown('<div class="step-header">📈 Step 3: Market Prices & Trends for Your Crops</div>', unsafe_allow_html=True)
    
    data = st.session_state.customer_data
    crops = st.session_state.recommended_crops
    
    if not crops:
        st.warning("⚠️ No crops to analyze. Going back...")
        time.sleep(2)
        st.session_state.workflow_step = 2
        st.rerun()
    
    st.info(f"💰 We'll check current market prices and trends for all {len(crops)} recommended crops to help you plan better.")
    
    # Show which crops will be analyzed
    st.markdown("### 🌾 Crops to Analyze:")
    cols = st.columns(min(len(crops), 4))
    for idx, crop in enumerate(crops):
        with cols[idx % 4]:
            st.info(f"**{idx + 1}.** {crop}")
    
    st.markdown("---")
    
    # Auto-analyze all crops
    if len(st.session_state.market_results) < len(crops):
        if st.button("🚀 Analyze All Crop Markets", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for idx, crop in enumerate(crops):
                status_text.text(f"🤖 Analyzing market for {crop}... ({idx + 1}/{len(crops)})")
                progress_bar.progress((idx + 1) / len(crops))
                
                try:
                    response = requests.post(
                        f"{API_URL}/market_predict",
                        json={"commodity": crop},
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        st.session_state.market_results[crop] = response.json()
                    else:
                        st.session_state.market_results[crop] = {
                            "error": response.json().get('detail', 'Error')
                        }
                
                except Exception as e:
                    st.session_state.market_results[crop] = {"error": str(e)}
                
                time.sleep(0.5)
            
            status_text.text("✅ All market analyses complete!")
            st.success("✅ Market analysis complete for all crops!")
            
            time.sleep(1)
            st.rerun()
    
    # Display results
    if len(st.session_state.market_results) > 0:
        st.success(f"✅ Market Analysis Complete for {len(st.session_state.market_results)} Crops!")
        
        st.markdown("### 💰 Market Analysis Summary")
        
        # Create summary table
        summary_data = []
        for crop, result in st.session_state.market_results.items():
            if 'error' not in result:
                analysis = result.get('analysis', {})
                prediction = result.get('prediction', {})
                
                summary_data.append({
                    'Crop': crop,
                    'Current Price': f"${analysis.get('current_price', 'N/A')}",
                    'Trend': analysis.get('trend', 'N/A'),
                    '2Y Change': f"{analysis.get('change_percent', 0)}%",
                    'Action': prediction.get('action', 'N/A'),
                    'Confidence': prediction.get('confidence', 'N/A')
                })
        
        if summary_data:
            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Back to Analysis", use_container_width=True):
                st.session_state.workflow_step = 2
                st.rerun()
        
        with col3:
            if st.button("➡️ Find Grants", type="primary", use_container_width=True):
                st.session_state.workflow_step = 4
                st.rerun()

# ============================================
# STEP 4: GRANT & SUBSIDY FINDER (AGENT 3)
# ============================================
elif st.session_state.workflow_step == 4:
    st.markdown('<div class="step-header">💰 Step 4: Government Grants & Financial Support</div>', unsafe_allow_html=True)
    
    data = st.session_state.customer_data
    
    st.info("🏛️ We'll search for government programs, grants, and subsidies that can help fund your farming operations.")
    
    st.markdown("### 💰 Available Grant Programs")
    
    # Show profile-based recommendations
    experience = data.get('experience', 'Intermediate')
    location = data.get('location_name', 'your location')
    farm_size = data.get('farm_size', 0)
    
    st.markdown(f"""
    Based on your profile:
    - **Location:** {location}
    - **Experience:** {experience}
    - **Budget:** {data.get('budget', 'N/A')}
    - **Farm Size:** {farm_size} acres
    
    We'll search for relevant grants and subsidies...
    """)
    
    # Real FAISS-based Grant Search
    if not st.session_state.grant_results:
        if st.button("🔍 Search for Grants & Subsidies", type="primary", use_container_width=True):
            with st.spinner("🤖 Agent 3 is searching USDA grant databases..."):
                try:
                    import faiss
                    import numpy as np
                    from openai import OpenAI
                    
                    # Initialize OpenAI client with API key from environment
                    api_key = os.getenv("OPENAI_API_KEY")
                    if not api_key:
                        st.error("❌ OPENAI_API_KEY not found in environment!")
                        st.info("💡 Make sure .env file exists with OPENAI_API_KEY=your_key_here")
                        st.stop()
                    
                    client = OpenAI(api_key=api_key)
                    
                    # Load FAISS index and metadata from data folder
                    index = faiss.read_index("data/usda_grants.faiss")
                    with open("data/usda_grants_meta.json", "r", encoding="utf-8") as f:
                        import json
                        programs_meta = json.load(f)
                    
                    with open("data/usda_grants.json", "r", encoding="utf-8") as f:
                        programs_full = json.load(f)
                    
                    # Build search query based on profile
                    query_parts = []
                    
                    if experience == "Beginner":
                        query_parts.append("beginning farmer new rancher startup loans")
                    
                    if farm_size < 50:
                        query_parts.append("small farm microloans")
                    elif farm_size > 500:
                        query_parts.append("large scale commercial operations")
                    
                    # Add crop-specific queries if available
                    if st.session_state.recommended_crops:
                        crops = " ".join(st.session_state.recommended_crops[:2])
                        query_parts.append(f"{crops} specialty crops")
                    
                    query_parts.append("operating loans grants subsidies")
                    
                    query = " ".join(query_parts)
                    
                    # Create embedding using new OpenAI client
                    response = client.embeddings.create(
                        model="text-embedding-3-large",
                        input=query
                    )
                    q_emb = np.array(response.data[0].embedding).astype("float32")
                    
                    # Search FAISS
                    D, I = index.search(np.array([q_emb]), min(5, len(programs_meta)))
                    
                    # Calculate match scores based on profile
                    def calculate_match_score(program, profile):
                        score = 50  # Base score
                        
                        eligibility = " ".join(program.get("eligibility", [])).lower()
                        summary = program.get("summary", "").lower()
                        
                        # Boost for beginning farmers
                        if profile.get("experience") == "Beginner" and ("beginning" in eligibility or "new farmer" in summary):
                            score += 30
                        
                        # Boost for farm size match
                        farm_size = profile.get("farm_size", 0)
                        if farm_size < 50 and "small" in summary:
                            score += 15
                        
                        # Boost for operating expense needs
                        if "operating" in summary or "expense" in summary:
                            score += 10
                        
                        # Boost for year-round availability
                        if program.get("year_round_application"):
                            score += 10
                        
                        return min(score, 100)
                    
                    # Build results
                    grants = []
                    for idx, distance in zip(I[0], D[0]):
                        if distance < 1.5:  # Relevance threshold
                            program = programs_full[idx]
                            
                            match_score = calculate_match_score(program, data)
                            
                            grants.append({
                                "name": program.get("program_name"),
                                "agency": program.get("agency"),
                                "amount": program.get("funding_amount"),
                                "match_score": match_score,
                                "eligibility": program.get("eligibility", []),
                                "deadline": program.get("application_deadlines"),
                                "type": program.get("program_type"),
                                "url": program.get("official_url"),
                                "summary": program.get("summary"),
                                "required_documents": program.get("required_documents", []),
                                "contact_info": program.get("contact_info"),
                                "distance": float(distance),
                                "confidence": 1 / (1 + distance)
                            })
                    
                    # Sort by match score
                    grants.sort(key=lambda x: x['match_score'], reverse=True)
                    
                    st.session_state.grant_results = grants
                    st.success(f"✅ Found {len(grants)} relevant grant opportunities!")
                    
                    time.sleep(1)
                    st.rerun()
                    
                except FileNotFoundError:
                    st.error("❌ Grant database files not found. Please ensure data/usda_grants.faiss, data/usda_grants_meta.json, and data/usda_grants.json exist in the project.")
                except Exception as e:
                    st.error(f"❌ Error searching grants: {str(e)}")
                    # Fallback to basic recommendations
                    st.warning("Showing basic recommendations instead...")
                    grants = []
                    if experience == "Beginner":
                        grants.append({
                            "name": "Beginning Farmers and Ranchers Loans",
                            "agency": "USDA Farm Service Agency (FSA)",
                            "amount": "Ownership: up to $600K; Operating: up to $400K",
                            "match_score": 90,
                            "eligibility": ["Less than 10 years farming experience"],
                            "deadline": "Continuous; funds reserved until April 1 annually",
                            "type": "Loan",
                            "url": "https://www.fsa.usda.gov/programs-and-services/beginning-farmers-and-ranchers"
                        })
                    grants.append({
                        "name": "Farm Operating Loans",
                        "agency": "USDA Farm Service Agency (FSA)",
                        "amount": "Direct: up to $400,000; Guaranteed: up to $2,251,000",
                        "match_score": 80,
                        "eligibility": ["Family farmers or ranchers"],
                        "deadline": "Year-round; processing 30-60 days",
                        "type": "Loan",
                        "url": "https://www.fsa.usda.gov/programs-and-services/farm-loan-programs/farm-operating-loans"
                    })
                    st.session_state.grant_results = grants
    
    # Display grant results
    if st.session_state.grant_results:
        st.success(f"✅ Found {len(st.session_state.grant_results)} Grant Opportunities!")
        
        st.markdown("---")
        
        for idx, grant in enumerate(st.session_state.grant_results, 1):
            match_score = grant.get('match_score', 50)
            
            # Color code
            if match_score >= 85:
                badge = "🟢 Excellent Match"
                color = "green"
            elif match_score >= 70:
                badge = "🟡 Good Match"
                color = "orange"
            else:
                badge = "🔵 Possible Match"
                color = "blue"
            
            with st.expander(f"{badge}: {grant['name']}", expanded=(idx <= 2)):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {grant['name']}")
                    st.markdown(f"**Agency:** {grant['agency']}")
                    st.markdown(f"**Type:** {grant['type']}")
                    st.markdown(f"**Funding Amount:** {grant['amount']}")
                    st.markdown(f"**Deadline:** {grant['deadline']}")
                    
                    # Show summary if available
                    if grant.get('summary'):
                        st.info(f"**Summary:** {grant['summary']}")
                    
                    st.markdown("**Eligibility Requirements:**")
                    for req in grant['eligibility'][:5]:  # Show top 5
                        st.markdown(f"- {req}")
                    
                    # Show search confidence
                    if grant.get('confidence'):
                        st.caption(f"Search Relevance: {grant['confidence']:.0%}")
                
                with col2:
                    st.metric("Match Score", f"{match_score}%")
                    
                    if match_score >= 85:
                        st.success("Highly Recommended")
                    elif match_score >= 70:
                        st.info("Worth Applying")
                    else:
                        st.warning("Consider Carefully")
                    
                    st.markdown("---")
                    
                    st.link_button(
                        "📄 View Details",
                        grant['url'],
                        use_container_width=True
                    )
                
                st.markdown("---")
                
                # Show required documents if available
                if grant.get('required_documents'):
                    st.markdown("**📋 Required Documents:**")
                    for doc in grant['required_documents']:
                        st.markdown(f"- {doc}")
                
                # Contact info
                if grant.get('contact_info'):
                    st.markdown(f"**📞 Contact:** {grant['contact_info']}")
                
                # Generate application checklist
                st.markdown("**✅ Application Checklist:**")
                checklist = f"""
- [ ] Review full eligibility requirements at {grant['url']}
- [ ] Check application deadline: {grant['deadline']}
- [ ] Gather required documents (see list above)
- [ ] Prepare farm/business plan
- [ ] Contact {grant['agency']} for guidance
- [ ] Submit application through official portal
"""
                st.markdown(checklist)
                
                # Download option
                checklist_file = f"""# Application Checklist for {grant['name']}

## Program Information
- **Agency:** {grant['agency']}
- **Type:** {grant['type']}
- **Funding:** {grant['amount']}
- **Deadline:** {grant['deadline']}

## Eligibility Requirements
{chr(10).join(f"- {req}" for req in grant['eligibility'])}

## Required Documents
{chr(10).join(f"- {doc}" for doc in grant.get('required_documents', ['See program website']))}

## Application Steps
1. Review full program details at: {grant['url']}
2. Verify you meet all eligibility requirements
3. Gather all required documents
4. Prepare detailed farm/business plan
5. Contact {grant.get('contact_info', 'local USDA office')} for guidance
6. Submit application before deadline: {grant['deadline']}

## Notes
- Match Score: {match_score}%
- Generated: {datetime.now().strftime("%Y-%m-%d")}
"""
                
                st.download_button(
                    "⬇️ Download Checklist",
                    data=checklist_file,
                    file_name=f"{grant['name'].replace(' ', '_')}_checklist.md",
                    mime="text/markdown",
                    key=f"download_grant_{idx}",
                    use_container_width=True
                )
        
        # Navigation
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button("⬅️ Back to Markets", use_container_width=True):
                st.session_state.workflow_step = 3
                st.rerun()
        
        with col3:
            if st.button("➡️ Final Report", type="primary", use_container_width=True):
                st.session_state.workflow_step = 5
                st.rerun()

# ============================================
# STEP 5: FINAL INTEGRATED REPORT
# ============================================
elif st.session_state.workflow_step == 5:
    st.markdown('<div class="step-header">📋 Step 5: Your Personalized Farming Action Plan</div>', unsafe_allow_html=True)
    
    report_time = datetime.now().strftime("%B %d, %Y at %H:%M:%S")
    st.success(f"✅ **Your Custom Plan Ready:** {report_time}")
    
    data = st.session_state.customer_data
    soil_result = st.session_state.soil_result
    market_results = st.session_state.market_results
    grant_results = st.session_state.grant_results
    
    # Executive Summary
    st.markdown("## 📋 Executive Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 👨‍🌾 Farm Profile")
        st.markdown(f"""
        - **Location:** {data.get('location_name', 'Custom')}
        - **Farm Size:** {data.get('farm_size')} acres
        - **Experience:** {data.get('experience')}
        - **Risk Tolerance:** {data.get('risk_tolerance')}
        - **Budget:** {data.get('budget')}
        """)
    
    with col2:
        st.markdown("### 🌱 Analysis Results")
        env = soil_result.get("environmental_summary", {})
        st.markdown(f"""
        - **Soil Type:** {env.get('soil_type', 'Unknown')}
        - **Temperature:** {env.get('temperature', 'N/A')}°C
        - **Crops Recommended:** {len(st.session_state.recommended_crops)}
        - **Market Analyses:** {len(market_results)}
        """)
    
    with col3:
        st.markdown("### 💰 Funding Opportunities")
        st.markdown(f"""
        - **Grants Found:** {len(grant_results)}
        - **Total Funding:** $500K+ available
        - **Best Match:** {grant_results[0]['match_score']}% if grant_results else 'N/A'
        - **Application Deadline:** Rolling
        """)
    
    # Top Recommendation
    st.markdown("---")
    st.markdown("## 🎯 #1 Recommended Action Plan")
    
    if st.session_state.recommended_crops and market_results:
        top_crop = st.session_state.recommended_crops[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"### 🌾 Recommended Crop: {top_crop}")
            
            # Find agronomic data
            recs = soil_result.get('recommendations', [])
            if isinstance(recs, list) and len(recs) > 0:
                rec = recs[0]
                st.success(f"**Why:** {rec.get('reason', 'Well-suited')}")
                st.warning(f"**Risk:** {rec.get('risk', 'Standard')}")
        
        with col2:
            st.markdown("### 💰 Market Outlook")
            if top_crop in market_results:
                analysis = market_results[top_crop].get('analysis', {})
                prediction = market_results[top_crop].get('prediction', {})
                
                st.metric("Current Price", f"${analysis.get('current_price', 'N/A')}")
                st.metric("Trend", analysis.get('trend', 'N/A'))
                
                action = prediction.get('action', 'N/A')
                if action == 'BUY':
                    st.success(f"**Signal:** {action} ✅")
                else:
                    st.warning(f"**Signal:** {action}")
    
    # Funding Options
    st.markdown("---")
    st.markdown("## 💰 Top Funding Options")
    
    if grant_results:
        for grant in grant_results[:3]:
            with st.expander(f"💰 {grant['name']} - {grant['amount']}", expanded=False):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**Agency:** {grant['agency']}")
                    st.markdown(f"**Type:** {grant['type']}")
                    st.markdown(f"**Deadline:** {grant['deadline']}")
                with col2:
                    st.metric("Match", f"{grant['match_score']}%")
                    st.link_button("Apply", grant['url'], use_container_width=True)
    
    # Top Recommendation
    st.markdown("---")
    st.markdown("## 🎯 Your Best Bet: Top Recommendation")
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("⬅️ Back", use_container_width=True):
            st.session_state.workflow_step = 4
            st.rerun()
    
    with col3:
        if st.button("🔄 New Analysis", use_container_width=True):
            st.session_state.workflow_step = 1
            st.session_state.customer_data = {}
            st.session_state.soil_result = None
            st.session_state.market_results = {}
            st.session_state.recommended_crops = []
            st.session_state.grant_results = []
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6D4C41; padding: 2rem; background: linear-gradient(135deg, #F5F5DC 0%, #FAFAF0 100%); border-radius: 12px; border-top: 4px solid #2E7D32;'>
    <h3 style='color: #2E7D32; margin-bottom: 1rem;'>🌾 Agricultural Advisory System 🚜</h3>
    <p style='font-size: 1.1rem; margin: 0.5rem 0;'><strong>Helping Farmers Grow Better, Farm Smarter</strong></p>
    <p style='font-size: 0.95rem; color: #8D6E63; margin: 1rem 0;'>
        Powered by AI • Real-time Data • Trusted by Farmers
    </p>
    <p style='font-size: 0.85rem; color: #A1887F; font-style: italic;'>
        "The best time to plant a tree was 20 years ago. The second best time is now." - Chinese Proverb
    </p>
</div>
""", unsafe_allow_html=True)