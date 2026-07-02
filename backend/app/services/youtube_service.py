import httpx
from typing import List, Dict, Any
from ..config import settings

def format_subscribers(sub_count_str: str) -> str:
    if not sub_count_str or not sub_count_str.isdigit():
        return "Not Available"
    
    count = int(sub_count_str)
    if count >= 1_000_000:
        val = count / 1_000_000
        return f"{val:.1f}M" if val % 1 != 0 else f"{int(val)}M"
    elif count >= 1_000:
        val = count / 1_000
        return f"{val:.1f}K" if val % 1 != 0 else f"{int(val)}K"
    return str(count)

async def search_youtube_channels(prompt: str) -> List[Dict[str, Any]]:
    """
    Queries the YouTube Data API search endpoint to find channels and
    makes a batch request to retrieve custom handles and subscriber counts.
    """
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        print("[WARN] YouTube API key is missing.")
        return []

    candidates = []
    
    # 1. Formulation of search queries
    # Add variations: e.g., "Tamil parenting" or "Tamil parenting influencer"
    search_queries = [
        prompt,
        f"{prompt} channel"
    ]
    
    seen_channel_ids = set()
    
    async with httpx.AsyncClient() as client:
        for query in search_queries:
            try:
                # 2. Search for channels
                search_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "type": "channel",
                    "q": query,
                    "maxResults": 8,
                    "key": api_key
                }
                
                response = await client.get(search_url, params=params, timeout=10.0)
                if response.status_code != 200:
                    print(f"[ERROR] YouTube Search failed: {response.text}")
                    continue
                    
                data = response.json()
                items = data.get("items", [])
                
                channel_ids = []
                channel_metadata = {}
                
                for item in items:
                    channel_id = item.get("id", {}).get("channelId", "")
                    if not channel_id or channel_id in seen_channel_ids:
                        continue
                        
                    snippet = item.get("snippet", {})
                    channel_ids.append(channel_id)
                    channel_metadata[channel_id] = {
                        "name": snippet.get("title", ""),
                        "bio": snippet.get("description", ""),
                        "profile_url": f"https://www.youtube.com/channel/{channel_id}"
                    }
                    seen_channel_ids.add(channel_id)
                
                if not channel_ids:
                    continue
                    
                # 3. Retrieve stats & customUrl handles for these channels
                stats_url = "https://www.googleapis.com/youtube/v3/channels"
                stats_params = {
                    "part": "statistics,snippet",
                    "id": ",".join(channel_ids),
                    "key": api_key
                }
                
                stats_response = await client.get(stats_url, params=stats_params, timeout=10.0)
                if stats_response.status_code != 200:
                    print(f"[ERROR] YouTube Channels Info failed: {stats_response.text}")
                    # Default without statistics
                    for cid in channel_ids:
                        metadata = channel_metadata[cid]
                        candidates.append({
                            "name": metadata["name"],
                            "username": cid,
                            "platform": "YouTube",
                            "profile_url": metadata["profile_url"],
                            "bio": metadata["bio"],
                            "followers": "Not Available"
                        })
                    continue
                    
                stats_data = stats_response.json()
                channel_details = stats_data.get("items", [])
                
                for detail in channel_details:
                    cid = detail.get("id", "")
                    meta = channel_metadata.get(cid)
                    if not meta:
                        continue
                        
                    snippet = detail.get("snippet", {})
                    statistics = detail.get("statistics", {})
                    
                    # Try to extract the custom handle (e.g. @tamilparenting -> tamilparenting)
                    custom_url = snippet.get("customUrl", "")
                    username = custom_url.replace("@", "") if custom_url else cid
                    
                    sub_count_str = statistics.get("subscriberCount", "")
                    followers = format_subscribers(sub_count_str)
                    
                    candidates.append({
                        "name": meta["name"],
                        "username": username,
                        "platform": "YouTube",
                        "profile_url": meta["profile_url"],
                        "bio": meta["bio"] if meta["bio"] else snippet.get("description", ""),
                        "followers": followers
                    })
                    
            except Exception as e:
                print(f"[ERROR] YouTube channel fetch error: {e}")
                
    return candidates
