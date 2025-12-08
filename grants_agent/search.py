import requests
from config.settings import BRAVE_API_KEY

def web_search_brave(query, num_results=5):
    """Search using Brave Search API"""
    if not BRAVE_API_KEY:
        raise ValueError("BRAVE_API_KEY not found!")
    
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
            raise ValueError("Invalid Brave API key")
        elif e.response.status_code == 429:
            raise ValueError("Rate limit exceeded")
        else:
            raise Exception(f"Brave API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Web search error: {str(e)}")