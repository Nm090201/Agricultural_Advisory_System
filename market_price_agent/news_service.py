from duckduckgo_search import DDGS
from datetime import datetime

def get_market_news(commodity: str, limit=5):
    """
    Fetches recent news headlines for a commodity using DuckDuckGo.
    Returns a list of strings (Headline - Source).
    """
    current_year = datetime.now().year
    query = f"{commodity} price news {current_year} market analysis"
    
    news_items = []
    try:
        with DDGS(timeout=10) as ddgs:
            results = list(ddgs.news(keywords=query, max_results=limit))
            
        for r in results:
            title = r.get('title', '')
            source = r.get('source', 'Unknown')
            date = r.get('date', '')
            # Clean up date if possible, but raw string is fine for LLM
            news_items.append(f"- {title} ({source})")
            
    except Exception as e:
        print(f"News Search Error: {e}")
        return ["Unable to fetch live news."]

    if not news_items:
        return ["No recent news found."]
        
    return news_items
