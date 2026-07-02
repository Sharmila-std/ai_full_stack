import json
from typing import List, Dict, Any
from groq import AsyncGroq
from ..config import settings

async def evaluate_candidates(prompt: str, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Calls Groq LLM to evaluate candidates against the search prompt.
    Uses batch JSON prompt format to minimize API round-trips and cost.
    """
    api_key = settings.GROQ_API_KEY
    if not api_key:
        print("[WARN] Groq API key is missing.")
        # If API key is missing, mock matching to keep MVP running
        return [
            {**c, "match_score": 85, "match_reason": f"Mock Match: Matches prompt '{prompt}'."}
            for c in candidates
        ]

    if not candidates:
        return []

    client = AsyncGroq(api_key=api_key)

    # Compile candidates for the prompt
    compact_candidates = [
        {
            "name": c["name"],
            "platform": c["platform"],
            "profile_url": c["profile_url"],
            "bio": c["bio"]
        }
        for c in candidates
    ]

    system_prompt = (
        "You are an AI Influencer Matcher. Your task is to evaluate a list of social media profiles "
        "and determine whether they match the user's discovery request.\n\n"
        "Rules:\n"
        "1. Focus strictly on whether the profile niche, language, and location (derived from bio or name) "
        "match the request.\n"
        "2. Provide a numeric match score between 0 and 100.\n"
        "3. Provide a concise, professional reason (1-2 sentences) explaining why they match or do not match.\n"
        "4. Respond ONLY with a valid JSON object matching the schema below. No other text.\n\n"
        "Schema:\n"
        "{\n"
        "  \"evaluations\": [\n"
        "    {\n"
        "      \"profile_url\": \"string\",\n"
        "      \"match\": boolean,\n"
        "      \"match_score\": integer,\n"
        "      \"reason\": \"string\"\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    user_content = {
        "user_request": prompt,
        "candidates": compact_candidates
    }

    try:
        # Groq Llama 3 70B
        chat_completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_content)}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
            temperature=0.1,
            timeout=15.0
        )
        
        response_text = chat_completion.choices[0].message.content
        result_data = json.loads(response_text)
        evaluations_list = result_data.get("evaluations", [])
        
        # Map evaluations back to candidates
        eval_map = {item["profile_url"]: item for item in evaluations_list if "profile_url" in item}
        
        matched_results = []
        for c in candidates:
            eval_info = eval_map.get(c["profile_url"])
            if eval_info and eval_info.get("match", False):
                matched_results.append({
                    **c,
                    "match_score": eval_info.get("match_score", 0),
                    "match_reason": eval_info.get("reason", "Matches search criteria.")
                })
                
        # Sort by match score descending
        matched_results.sort(key=lambda x: x["match_score"], reverse=True)
        return matched_results

    except Exception as e:
        print(f"[ERROR] Groq matching error: {e}")
        # Fallback: return top 5 candidates as mock matches so application doesn't crash on API failure
        return [
            {**c, "match_score": 75, "match_reason": "Evaluation fallback due to API rate-limit or error."}
            for c in candidates[:8]
        ]
