"use client";

import React, { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import SearchForm from "@/components/SearchForm";
import ResultCard from "@/components/ResultCard";
import { Influencer } from "@/types";
import { Sparkles, HelpCircle, AlertCircle } from "lucide-react";

export default function DiscoverPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState<Influencer[]>([]);
  const [savedUrls, setSavedUrls] = useState<Set<string>>(new Set());
  const [error, setError] = useState("");

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  // Load existing CRM URLs on mount to avoid saving duplicates
  useEffect(() => {
    async function fetchSavedInfluencers() {
      try {
        const res = await fetch(`${apiBaseUrl}/api/crm`);
        if (res.ok) {
          const data: Influencer[] = await res.json();
          const urls = new Set(data.map((inf) => inf.profile_url));
          setSavedUrls(urls);
        }
      } catch (err) {
        console.error("Error loading CRM records:", err);
      }
    }
    fetchSavedInfluencers();
  }, [apiBaseUrl]);

  const handleSearch = async (prompt: string, platforms: string[]) => {
    setIsLoading(true);
    setError("");
    setResults([]);

    try {
      const res = await fetch(`${apiBaseUrl}/api/search`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ prompt, platforms }),
      });

      if (!res.ok) {
        const errDetail = await res.json();
        throw new Error(errDetail.detail || "Search request failed.");
      }

      const data = await res.json();
      setResults(data.results || []);
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to query the search API. Please check backend config.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveToCRM = async (influencer: Influencer): Promise<boolean> => {
    try {
      const res = await fetch(`${apiBaseUrl}/api/crm`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(influencer),
      });

      if (res.ok) {
        // Update local saved state
        setSavedUrls((prev) => {
          const next = new Set(prev);
          next.add(influencer.profile_url);
          return next;
        });
        return true;
      }
      return false;
    } catch (err) {
      console.error("Save error:", err);
      return false;
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 md:px-12 py-8 space-y-12">
        {/* Banner Section */}
        <div className="text-center space-y-4 max-w-2xl mx-auto">
          <div className="inline-flex items-center space-x-2 bg-primary/10 border border-primary/20 px-3 py-1.5 rounded-full text-xs font-semibold text-indigo-300">
            <Sparkles className="h-4.5 w-4.5 text-primary" />
            <span>AI-Driven Influencer Sourcing MVP</span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
            Discover Influencer Partners <br />
            <span className="gradient-text">Across the Web</span>
          </h1>
          <p className="text-muted-foreground">
            Describe the type of creator you're looking for. Our agent will query search engines, target active profiles, and filter them using Groq LLM reasoning.
          </p>
        </div>

        {/* Input Form */}
        <div className="max-w-3xl mx-auto w-full">
          <SearchForm onSearch={handleSearch} isLoading={isLoading} />
        </div>

        {/* Error State */}
        {error && (
          <div className="max-w-3xl mx-auto w-full p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-medium rounded-xl flex items-center space-x-2.5">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Loading Placeholders */}
        {isLoading && (
          <div className="space-y-6 max-w-5xl mx-auto">
            <h2 className="text-lg font-bold text-foreground">Scouting profiles...</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((idx) => (
                <div key={idx} className="w-full h-80 rounded-2xl border border-card-border/50 bg-card-bg/40 p-6 flex flex-col justify-between overflow-hidden">
                  <div className="space-y-4 w-full">
                    <div className="flex justify-between">
                      <div className="shimmer w-16 h-6 rounded" />
                      <div className="shimmer w-12 h-6 rounded" />
                    </div>
                    <div className="space-y-2">
                      <div className="shimmer w-1/2 h-5 rounded" />
                      <div className="shimmer w-1/3 h-4 rounded" />
                    </div>
                    <div className="shimmer w-full h-16 rounded" />
                  </div>
                  <div className="shimmer w-full h-10 rounded-xl" />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Results display */}
        {!isLoading && results.length > 0 && (
          <div className="space-y-6 max-w-7xl mx-auto">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-foreground flex items-center space-x-2">
                <span>Matching Candidates</span>
                <span className="text-xs font-normal text-muted-foreground bg-white/5 border border-card-border px-2 py-0.5 rounded-full">
                  {results.length} found
                </span>
              </h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {results.map((influencer, idx) => (
                <ResultCard
                  key={idx}
                  influencer={influencer}
                  isSaved={savedUrls.has(influencer.profile_url)}
                  onSave={handleSaveToCRM}
                />
              ))}
            </div>
          </div>
        )}

        {/* Empty search prompt state */}
        {!isLoading && results.length === 0 && (
          <div className="max-w-md mx-auto py-12 text-center text-muted-foreground flex flex-col items-center space-y-3">
            <HelpCircle className="h-10 w-10 text-muted-foreground/45" />
            <p className="text-sm">
              Ready to find talent. Enter a search prompt and select a channel above.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
