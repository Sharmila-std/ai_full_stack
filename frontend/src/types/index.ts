export interface Influencer {
  id?: string;
  name: string;
  username: string;
  platform: string;
  profile_url: string;
  bio?: string;
  followers?: string;
  match_score: number;
  match_reason?: string;
  created_at?: string;
}

export interface SearchRequest {
  prompt: string;
  platforms: string[];
}

export interface SearchResponse {
  results: Influencer[];
}
