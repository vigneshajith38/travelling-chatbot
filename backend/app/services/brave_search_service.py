import os
import urllib.parse
from typing import Dict, Any, List, Optional
from app.core.config import settings

BRAVE_LLM_CONTEXT_URL = "https://api.search.brave.com/res/v1/llm/context"
BRAVE_WEB_SEARCH_URL = "https://api.search.brave.com/res/v1/web/search"
BRAVE_LOCAL_SEARCH_URL = "https://api.search.brave.com/res/v1/local/pois"

def get_brave_api_key() -> str:
    """Retrieves the Brave Search API key from settings or environment."""
    key = getattr(settings, "BRAVE_API_KEY", "") or os.getenv("BRAVE_API_KEY", "")
    return key.strip()

def is_brave_available() -> bool:
    """Checks whether a valid Brave Search API key is configured."""
    key = get_brave_api_key()
    return bool(key and len(key) >= 10 and not key.startswith("your_"))

def search_llm_context(query: str, count: int = 5) -> Optional[Dict[str, Any]]:
    """
    Calls Brave LLM Context endpoint:
    GET https://api.search.brave.com/res/v1/llm/context
    Retrieves web grounding contexts and extracts optimized specifically for LLMs.
    """
    key = get_brave_api_key()
    if not key:
        return None

    try:
        import httpx
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": key,
            "User-Agent": "WanderWise-AI-Travel/2.0"
        }
        params = {
            "q": query.strip(),
            "count": max(1, min(10, count))
        }
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(BRAVE_LLM_CONTEXT_URL, headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                
                # Parse context extracts and references
                grounding = data.get("grounding", {})
                generic = grounding.get("generic", []) or []
                
                extracted_contexts = []
                sources = []
                for item in generic:
                    title = item.get("title", "")
                    url = item.get("url", "")
                    snippets = item.get("snippets", []) or []
                    text_blob = " ".join(snippets)
                    if url and url not in [s["url"] for s in sources]:
                        sources.append({"title": title, "url": url})
                    if text_blob:
                        extracted_contexts.append({
                            "title": title,
                            "url": url,
                            "content": text_blob
                        })

                return {
                    "source": "Brave LLM Context Engine",
                    "query": query,
                    "extracted_contexts": extracted_contexts,
                    "sources": sources,
                    "raw_context": "\n".join([f"• [{c['title']}]: {c['content']}" for c in extracted_contexts[:4]])
                }
            else:
                print(f"Brave LLM Context returned status {resp.status_code}: {resp.text[:120]}")
    except Exception as e:
        print(f"Brave LLM Context search note: {e}")

    return None

def search_web(query: str, count: int = 5, search_filter: str = "web,locations") -> Optional[Dict[str, Any]]:
    """
    Calls Brave Web Search endpoint:
    GET https://api.search.brave.com/res/v1/web/search
    Retrieves traditional ranked web results, live URLs, snippets, and local places.
    """
    key = get_brave_api_key()
    if not key:
        return None

    try:
        import httpx
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": key,
            "User-Agent": "WanderWise-AI-Travel/2.0"
        }
        params = {
            "q": query.strip(),
            "count": max(1, min(10, count)),
            "result_filter": search_filter
        }
        with httpx.Client(timeout=5.0) as client:
            resp = client.get(BRAVE_WEB_SEARCH_URL, headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                
                web_results = []
                sources = []
                for r in data.get("web", {}).get("results", [])[:count]:
                    title = r.get("title", "")
                    url = r.get("url", "")
                    desc = r.get("description", "")
                    age = r.get("page_age", "")
                    web_results.append({
                        "title": title,
                        "url": url,
                        "snippet": desc,
                        "age": age
                    })
                    if url and url not in [s["url"] for s in sources]:
                        sources.append({"title": title, "url": url})

                # Extract local places if present in response
                locations = []
                for loc in data.get("locations", {}).get("results", []):
                    locations.append({
                        "title": loc.get("title"),
                        "address": loc.get("address", {}).get("streetAddress"),
                        "city": loc.get("address", {}).get("addressLocality"),
                        "rating": loc.get("rating", {}).get("ratingValue"),
                        "reviews": loc.get("rating", {}).get("ratingCount")
                    })

                return {
                    "source": "Brave Web Search API",
                    "query": query,
                    "results": web_results,
                    "sources": sources,
                    "locations": locations,
                    "summary_text": "\n".join([f"• [{r['title']}]({r['url']}): {r['snippet']}" for r in web_results[:4]])
                }
            else:
                print(f"Brave Web Search returned status {resp.status_code}: {resp.text[:120]}")
    except Exception as e:
        print(f"Brave Web Search note: {e}")

    return None

def search_places(query: str, count: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Queries Brave Local Places / POI Search:
    1. Tries GET https://api.search.brave.com/res/v1/local/pois
    2. Falls back to Web Search with locations filter if POI endpoint is unavailable.
    """
    key = get_brave_api_key()
    if not key:
        return None

    try:
        import httpx
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": key,
            "User-Agent": "WanderWise-AI-Travel/2.0"
        }
        params = {
            "q": query.strip(),
            "count": max(1, min(10, count))
        }
        with httpx.Client(timeout=4.0) as client:
            resp = client.get(BRAVE_LOCAL_SEARCH_URL, headers=headers, params=params)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for item in data.get("results", [])[:count]:
                    results.append({
                        "name": item.get("name"),
                        "address": item.get("address", {}).get("streetAddress"),
                        "city": item.get("address", {}).get("addressLocality"),
                        "rating": item.get("rating", {}).get("ratingValue"),
                        "phone": item.get("phone"),
                        "coordinates": item.get("coordinates")
                    })
                if results:
                    return results
    except Exception as e:
        print(f"Brave Place search note: {e}")

    # Fallback to web search with locations filter
    try:
        web_res = search_web(query, count=count, search_filter="locations")
        if web_res and web_res.get("locations"):
            return [
                {
                    "name": loc.get("title"),
                    "address": loc.get("address"),
                    "city": loc.get("city"),
                    "rating": loc.get("rating"),
                    "phone": None,
                    "coordinates": None
                }
                for loc in web_res["locations"][:count]
            ]
    except Exception as e:
        print(f"Brave Place fallback note: {e}")

    return None

def get_brave_travel_intelligence(destination: str, user_query: str = "") -> Dict[str, Any]:
    """
    Universal High-Level Brave Travel Intelligence Gateway:
    1. Tries Brave LLM Context endpoint for ground-truth synthesis.
    2. Falls back to Brave Web Search for live URLs and snippets.
    3. Returns structured context ready for injection into Gemini AI prompts.
    """
    if not is_brave_available():
        return {
            "status": "Inactive",
            "available": False,
            "grounding_context": "",
            "sources": []
        }

    clean_d = destination.split(",")[0].strip()
    
    # Formulate effective search query
    if user_query and any(w in user_query.lower() for w in ["ticket", "entry fee", "timings", "open", "weather", "safe", "best time", "food"]):
        search_prompt = f"{clean_d} travel {user_query}"
    else:
        search_prompt = f"{clean_d} top attractions opening hours ticket prices tourism travel guide"

    # 1. Try LLM Context endpoint first
    llm_res = search_llm_context(search_prompt, count=4)
    if llm_res and llm_res.get("extracted_contexts"):
        context_lines = [f"• {c['title']}: {c['content']}" for c in llm_res["extracted_contexts"][:4]]
        grounding_text = (
            f"[REAL-TIME WEB GROUNDING FROM BRAVE SEARCH API (llm/context) for {clean_d}:\n"
            f"{chr(10).join(context_lines)}\n"
            f"Use these verified live facts to verify attraction existence, open hours, and entry fees.]"
        )
        return {
            "status": "Active",
            "available": True,
            "endpoint_used": "llm/context",
            "grounding_context": grounding_text,
            "sources": llm_res.get("sources", []),
            "contexts": llm_res.get("extracted_contexts", [])
        }

    # 2. Try Web Search endpoint fallback
    web_res = search_web(search_prompt, count=4)
    if web_res and web_res.get("results"):
        context_lines = [f"• {r['title']} ({r['url']}): {r['snippet']}" for r in web_res["results"][:4]]
        grounding_text = (
            f"[REAL-TIME WEB GROUNDING FROM BRAVE WEB SEARCH API for {clean_d}:\n"
            f"{chr(10).join(context_lines)}\n"
            f"Ground your answer in these verified web snippets.]"
        )
        return {
            "status": "Active",
            "available": True,
            "endpoint_used": "web/search",
            "grounding_context": grounding_text,
            "sources": web_res.get("sources", []),
            "results": web_res.get("results", [])
        }

    return {
        "status": "Active",
        "available": True,
        "endpoint_used": None,
        "grounding_context": "",
        "sources": []
    }
