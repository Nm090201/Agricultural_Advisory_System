# 🌾 Agricultural Advisory System

**AI-powered farming recommendations through multi-agent analysis**

---

## Overview

The Agricultural Advisory System is an integrated platform that provides farmers with comprehensive decision support across crop selection, market analysis, and funding opportunities. The system employs three specialized AI agents to deliver personalized agricultural guidance.

---

## System Components

### Agent 1: Soil & Climate Analyzer
Evaluates environmental conditions and recommends suitable crops based on real-time soil composition and climatic data.

### Agent 2: Market Price Predictor
Analyzes commodity pricing trends, provides market forecasts, and delivers buy/sell recommendations.

### Agent 3: Grant Finder
Identifies relevant government funding programs and calculates personalized eligibility match scores.

---

## User Requirements

The system requires five essential inputs:
1. Geographic location
2. Farm size (acres)
3. Farming experience level
4. Risk tolerance
5. Investment budget

---

## System Outputs

### Environmental Analysis
- Soil type classification and composition
- Climate suitability assessment
- Crop recommendations with justification

### Market Intelligence
- Current commodity prices
- Multi-year price trend analysis
- Seasonality patterns
- Market outlook and recommendations

### Funding Opportunities
- USDA program identification
- Match probability scoring
- Eligibility requirements
- Application guidelines

---

## Technical Architecture

### Backend Services
FastAPI-based RESTful API providing endpoints for environmental analysis and market prediction.

### Frontend Interface
Streamlit-based progressive web application with guided workflow and real-time data visualization.

### Data Infrastructure
FAISS vector database for semantic grant search with OpenAI embedding integration.

---

## Data Sources

- USDA National Agricultural Statistics Service
- Open-Meteo weather services
- ISRIC World Soil Information
- OpenStreetMap geocoding
- Official USDA program databases

---

## Workflow Process

1. User profile collection
2. Environmental analysis and crop recommendation
3. Automated market analysis for recommended crops
4. Grant program search and matching
5. Integrated advisory report generation

---

## Security & Privacy

- Secure API key management
- Session-based processing
- No permanent data retention
- User information not shared

---

## System Benefits

- Comprehensive multi-factor analysis
- Real-time data integration
- Personalized recommendations
- Evidence-based decision support
- Streamlined grant discovery
- Professional-level insights

---

## Disclaimer

This system provides advisory information for decision support purposes. Users should verify recommendations with local agricultural experts and confirm grant eligibility through official USDA channels before taking action.

---

**Agricultural Advisory System** | Supporting informed farming decisions through intelligent technology