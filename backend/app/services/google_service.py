import httpx
import re
from typing import List, Dict, Any, Set
from urllib.parse import urlparse
from ..config import settings

# Regex to match valid profiles
INSTAGRAM_PROFILE_RE = re.compile(r"^https?://(?:www\.)?instagram\.com/([a-zA-Z0-9_\.]+)/?$")

def get_numeric_followers(followers_str: str) -> int:
    if not followers_str or followers_str == "Not Available":
        return -1
    
    followers_str = followers_str.lower().strip()
    followers_str = followers_str.replace(",", "").replace(" ", "")
    
    try:
        if followers_str.endswith("m"):
            return int(float(followers_str[:-1]) * 1_000_000)
        elif followers_str.endswith("k"):
            return int(float(followers_str[:-1]) * 1_000)
        elif followers_str.endswith("b"):
            return int(float(followers_str[:-1]) * 1_000_000_000)
        else:
            return int(float(followers_str))
    except Exception:
        return -1
TIKTOK_PROFILE_RE = re.compile(r"^https?://(?:www\.)?tiktok\.com/(@[a-zA-Z0-9_\-\.]+)/?$")
TWITTER_PROFILE_RE = re.compile(r"^https?://(?:www\.)?(?:twitter|x)\.com/([a-zA-Z0-9_]+)/?$")

# Regex to check followers from snippet
FOLLOWER_RE = re.compile(r"\b([0-9\.]+[KMBkmb]?)\s*(?:[Ff]ollowers|[Ss]ubscribers|[Ss]ubs)\b")

def clean_url(url: str) -> str:
    # Remove query params (like fbclid, UTM, etc.)
    return url.split("?")[0].rstrip("/")

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

def is_valid_profile(platform: str, url: str) -> bool:
    url_cleaned = clean_url(url)
    
    # Parse URL segments to avoid false positives (e.g. usernames containing blacklisted words like "shorts")
    parsed = urlparse(url_cleaned)
    path_segments = [seg.lower().strip() for seg in parsed.path.split("/") if seg.strip()]
    
    # Expanded blacklist of invalid routes, posts, tags and generic pages
    blacklist = {
        "reel", "reels", "stories", "story", "post", "posts", "explore",
        "accounts", "login", "signup", "about", "help", "support",
        "privacy", "terms", "directory", "hashtag", "tags", "search",
        "oauth", "feed", "watch", "shorts", "popular", "developer", "blog", "legal"
    }
    
    # Reject if any URL path segment is in the blacklist
    if any(seg in blacklist for seg in path_segments):
        return False
        
    # Reject if the username itself matches any generic/system page names
    username = extract_username(platform, url_cleaned)
    if not username or username.lower() in blacklist:
        return False
        
    # Positive validation of profile patterns
    if platform.lower() == "instagram":
        return bool(INSTAGRAM_PROFILE_RE.match(url_cleaned))
    elif platform.lower() == "tiktok":
        return bool(TIKTOK_PROFILE_RE.match(url_cleaned))
    elif platform.lower() == "twitter":
        return bool(TWITTER_PROFILE_RE.match(url_cleaned))
        
    return False

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
    Generates template queries for Serper, queries Serper, parses results, and extracts candidates.
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
            # Generate 4 robust templates per platform to increase coverage while focusing on creators
            queries.append((platform_name, f"{prompt} {platform_name} creator"))
            queries.append((platform_name, f"{prompt} {platform_name} influencer"))
            queries.append((platform_name, f"{prompt} content creator"))
            queries.append((platform_name, f"{site_filter} {prompt}"))

    if not queries:
        queries.append(("Instagram", f"site:instagram.com {prompt}"))
        queries.append(("TikTok", f"site:tiktok.com {prompt}"))

    candidates = []
    seen_urls: Set[str] = set()

    async with httpx.AsyncClient() as client:
        # Sequential execution of templates
        for platform_name, query_str in queries:
            try:
                url = "https://google.serper.dev/search"
                headers = {
                    "X-API-KEY": api_key,
                    "Content-Type": "application/json"
                }
                payload = {
                    "q": query_str,
                    "num": 8  # Limit candidate queries to prevent heavy payload overhead
                }
                
                print(f"[DEBUG] Querying Serper: '{query_str}'")
                response = await client.post(url, headers=headers, json=payload, timeout=10.0)
                if response.status_code != 200:
                    print(f"[ERROR] Serper search failed: {response.text}")
                    continue
                
                data = response.json()
                organic_results = data.get("organic", [])
                
                for item in organic_results:
                    link = item.get("link", "")
                    title = item.get("title", "")
                    snippet = item.get("snippet", "")
                    
                    if not link:
                        continue
                        
                    link_cleaned = clean_url(link)
                    
                    if link_cleaned in seen_urls:
                        continue
                    
                    # Verify using positive and blacklist rules
                    if not is_valid_profile(platform_name, link_cleaned):
                        continue
                        
                    username = extract_username(platform_name, link_cleaned)
                    if not username:
                        continue
                        
                    name = extract_name_from_title(title, username)
                    followers = parse_follower_count(snippet)
                    if followers == "Not Available":
                        followers = parse_follower_count(title)
                        
                    # Filter out profiles explicitly parsed to have fewer than 2,000 followers
                    num_followers = get_numeric_followers(followers)
                    if 0 <= num_followers < 2000:
                        continue
                        
                    candidates.append({
                        "name": name,
                        "username": username,
                        "platform": platform_name,
                        "profile_url": link_cleaned,
                        "bio": snippet if snippet else f"Profile page for {name}.",
                        "followers": followers
                    })
                    seen_urls.add(link_cleaned)
                    
            except Exception as e:
                print(f"[ERROR] Failed searching query '{query_str}': {e}")
                
    return candidates
