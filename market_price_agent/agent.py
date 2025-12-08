import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from .nass_service import get_historical_prices
from .analysis_service import analyze_price_trends
from .news_service import get_market_news
from datetime import datetime

load_dotenv()

def predict_market(commodity: str):
    """
    Orchestrates the market prediction workflow.
    """
    # 1. Get Data (Last 2 years)
    current_year = datetime.now().year
    prices = get_historical_prices(commodity, current_year - 2, current_year)
    
    # 2. Get News (Always fetch news, even if NASS fails)
    news_headlines = get_market_news(commodity)
    news_summary = "\n".join(news_headlines[:3]) # Top 3 headlines
    
    if not prices:
        # FALLBACK: If NASS has no data (e.g. "Rye"), ask LLM for general market knowledge.
        print(f"⚠️ No NASS data for {commodity}. Switching to LLM General Knowledge.")
        
        prompt = f"""
        You are an Expert Agricultural Economist.
        
        **Commodity**: {commodity}
        **Data Status**: No specific NASS price data available for this niche crop.
        
        **Recent News**:
        {news_summary}
        
        **Task**:
        Based on the recent news above AND your general knowledge, provide a market outlook.
        
        **Format**: JSON
        {{
            "prediction": "General market outlook (referencing news if relevant).",
            "confidence": "Low (News + General Knowledge)",
            "action": "RESEARCH LOCAL MARKET",
            "reasoning": "Explain drivers based on the news provided."
        }}
        """
        
        analysis = {
            "current_price": "N/A",
            "trend": "Unknown",
            "change_percent": 0,
            "history_summary": "No NASS data available.",
            "seasonality": "N/A"
        }
    else:
        # Standard Flow with Data
        analysis = analyze_price_trends(prices)
        
        prompt = f"""
        You are an Expert Agricultural Economist.
        
        **Commodity**: {commodity}
        **Historical Data**: {analysis['history_summary']}
        **Current Trend**: {analysis['trend']} ({analysis['change_percent']}%)
        **Current Price**: ${analysis['current_price']}
        **Average Price**: ${analysis['average_price']}
        **Seasonality**: {analysis['seasonality']}
        
        **Recent News**:
        {news_summary}
        
        **Task**:
        Predict the price movement for the next 3 months and recommend action.
        Explicitly mention if the News or Seasonality supports your prediction.
        
        **Format**: JSON
        {{
            "prediction": "Short sentence on expected price movement.",
            "confidence": "High/Medium/Low",
            "action": "SELL NOW / HOLD / BUY",
            "reasoning": "Concise explanation citing data/news."
        }}
        
        **IMPORTANT GUIDELINES**:
        - If the price trend is **Upward** (>5%) and Seasonality supports it, recommend **BUY**.
        - If the price trend is **Downward** (<-5%) and Seasonality supports it, recommend **SELL** (to cut losses) or **HOLD** (if bottoming out).
        - Do NOT default to "HOLD" unless the signals are truly conflicting. Be decisive.
        - If Confidence is High, the Action MUST be BUY or SELL.
        """
    
    # 3. LLM Prediction (Common for both flows)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY missing."}
        
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
    except Exception as e:
        result = {"error": f"LLM Error: {e}"}
        
    return {
        "commodity": commodity,
        "data_source": "USDA NASS (Live)" if prices else "LLM General Knowledge (Fallback)",
        "analysis": analysis,
        "prediction": result,
        "news": news_headlines,
        "price_data": prices # Return raw data for charting
    }
