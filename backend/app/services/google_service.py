import httpx
import re
from typing import List, Dict, Any, Set
from ..config import settings

# Regex to match valid profiles
INSTAGRAM_PROFILE_RE = re.compile(r"^https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_\.]+)/?$")
TIKTOK_PROFILE_RE = re.compile(r"^https?://(?:www\.)?tiktok\.com/(@[a-zA-Z0-9_\-\.]+)/?$")
TWITTER_PROFILE_RE = re.compile(r"^https?://(?:www\.)?(?:twitter|x)\.com/([a-zA-Z0-9_]+)/?$")

# Regex to check followers from snippet
FOLLOWER_RE = re.compile(r"\b([0-9\.]+[KMBkmb]?)\s*(?:[Ff]ollowers|[Ss]ubscribers|[Ss]ubs)\b")

def clean_url(url: str) -> str:
    # Remove query params (like fbclid, UTM, etc.)
    return url.split("?")[0].rstrip("/")

def is_valid_profile(platform: str, url: str) -> bool:
    url_cleaned = clean_url(url)
    
    # Exclude typical non-profile routes
    invalid_patterns = ["/reel/", "/p/", "/posts/", "/explore/", "/hashtag/", "/tag/", "/search", "/status/", "/watch"]
    if any(p in url_cleaned.lower() for p in invalid_patterns):
        return False
        
    if platform.lower() == "instagram":
        return bool(INSTAGRAM_PROFILE_RE.match(url_cleaned))
    elif platform.lower() == "tiktok":
        return bool(TIKTOK_PROFILE_RE.match(url_cleaned))
    elif platform.lower() == "twitter":
        return bool(TWITTER_PROFILE_RE.match(url_cleaned))
        
    return False

def extract_username(platform: str, url: str) -> str:
    url_cleaned = clean_url(url)
    if platform.lower() == "instagram":
        m = INSTAGRAM_PROFILE_RE.match(url_cleaned)
        return m.group(1) if m else ""
    elif platform.lower() == "tiktok":
        m = TIKTOK_PROFILE_RE.match(url_cleaned)
        return m.group(1) if m else ""
    elif platform.lower() == "twitter":
        m = TWITTER_PROFILE_RE.match(url_cleaned)
        return m.group(1) if m else ""
    return ""

def extract_name_from_title(title: str, username: str) -> str:
    # Clean standard title suffixes
    for suffix in ["• Instagram", "Instagram photos", "| Twitter", "Twitter", "| TikTok", "TikTok", "on Twitter", "on Instagram", "on TikTok"]:
        title = re.sub(re.escape(suffix), "", title, flags=re.IGNORECASE)
    
    # Remove usernames like (@handle)
    title = re.sub(r"\(@?[a-zA-Z0-9_\-\.]+\)", "", title)
    
    # Strip delimiters
    title = title.split("|")[0].split("-")[0].split("•")[0].strip()
    
    # Default back to username if title got cleared
    if not title or title.isspace():
        title = username
    return title

def parse_follower_count(text: str) -> str:
    match = FOLLOWER_RE.search(text)
    if match:
        return match.group(1)
    return "Not Available"

async def search_google_serper(prompt: str, platforms: List[str]) -> List[Dict[str, Any]]:
    """
    Generates queries for Serper, queries the Serper API, parses the outputs, and extracts candidate structures.
    """
    api_key = settings.SERPER_API_KEY
    if not api_key:
        print("[WARN] Serper API key is missing.")
        return []

    # Map request platforms to target domains
    platform_domains = {
        "instagram": ("Instagram", "site:instagram.com"),
        "tiktok": ("TikTok", "site:tiktok.com"),
        "twitter": ("Twitter", "site:twitter.com"),
        "x": ("Twitter", "site:x.com")
    }

    # Normalize requested platforms to lower
    req_platforms = [p.lower() for p in platforms]
    queries = []
    
    for p in req_platforms:
        if p in platform_domains:
            platform_name, site_filter = platform_domains[p]
            # Template 1: Exact target domain
            queries.append((platform_name, f"{prompt} {site_filter}"))
            # Template 2: General target keyword
            queries.append((platform_name, f"{prompt} {platform_name} influencer"))

    if not queries:
        # Fallback if no target platforms selected
        queries.append(("Instagram", f"{prompt} site:instagram.com"))
        queries.append(("TikTok", f"{prompt} site:tiktok.com"))

    candidates = []
    seen_urls: Set[str] = set()

    async with httpx.AsyncClient() as client:
        # For simplicity, query Serper sequentially or concurrently (since it's async)
        for platform_name, query_str in queries:
            try:
                url = "https://google.serper.dev/search"
                headers = {
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "q": query_str,
                    "num": 10
                }
                
                print(f"[DEBUG] Querying Serper: '{query_str}'")
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                print(f"[DEBUG] Serper status: {response.status_code}")
                if response.status_code != 200:
                    print(f"[ERROR] Serper search failed: {response.text}")
                    continue
                
                data = response.json()
                organic_results = data.get("organic", [])
                print(f"[DEBUG] Organic results count: {len(organic_results)}")
                
                for item in organic_results:
                    link = item.get("link", "")
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    
                    if not link:
                        continue
                        
                    link_cleaned = clean_url(link)
                    print(f"[DEBUG] Link found: {link_cleaned}")
                    
                    if link_cleaned in seen_urls:
                        print(f"[DEBUG] Link already seen: {link_cleaned}")
                        continue
                    
                    # Verify it matches our platform profile rules & doesn't contain noise
                    if not is_valid_profile(platform_name, link_cleaned):
                        print(f"[DEBUG] Link rejected by is_valid_profile: {link_cleaned} (platform: {platform_name})")
                        continue
                        
                    username = extract_username(platform_name, link_cleaned)
                    if not username:
                        print(f"[DEBUG] No username extracted from: {link_cleaned}")
                        continue
                        
                    name = extract_name_from_title(title, username)
                    followers = parse_follower_count(snippet)
                    if followers == "Not Available":
                        # Try parsing from title
                        followers = parse_follower_count(title)
                        
                    candidates.append({
                        "name": name,
                        "username": username,
                        "platform": platform_name,
                        "profile_url": link_cleaned,
                        "bio": snippet if snippet else f"Profile page for {name}.",
                        "followers": followers
                    })
                    print(f"[DEBUG] Added candidate: {name} (@{username}) - {platform_name}")
                    seen_urls.add(link_cleaned)
                    
            except Exception as e:
                print(f"[ERROR] Failed searching query '{query_str}': {e}")
                
    print(f"[DEBUG] Total Google candidates: {len(candidates)}")
    return candidates
