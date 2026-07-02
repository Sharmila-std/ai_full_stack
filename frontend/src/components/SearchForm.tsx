"use client";

import React, { useState } from "react";
import { Search, Loader2 } from "lucide-react";

interface SearchFormProps {
  onSearch: (prompt: string, platforms: string[]) => void;
  isLoading: boolean;
}

export default function SearchForm({ onSearch, isLoading }: SearchFormProps) {
  const [prompt, setPrompt] = useState("");
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([
    "Instagram",
    "YouTube",
  ]);

  const platforms = ["Instagram", "YouTube", "TikTok", "Twitter"];

  const handlePlatformToggle = (platform: string) => {
    if (selectedPlatforms.includes(platform)) {
      if (selectedPlatforms.length > 1) {
        setSelectedPlatforms(selectedPlatforms.filter((p) => p !== platform));
      }
    } else {
      setSelectedPlatforms([...selectedPlatforms, platform]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    onSearch(prompt.trim(), selectedPlatforms);
  };

  return (
    <form onSubmit={handleSubmit} className="w-full glass rounded-2xl p-6 md:p-8 space-y-6">
      <div className="space-y-2">
        <label htmlFor="prompt" className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Natural Language Prompt
        </label>
        <div className="relative">
          <input
            id="prompt"
            type="text"
            required
            disabled={isLoading}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="e.g. Find Tamil parenting influencers in India..."
            className="w-full bg-[#0d131f] border border-card-border rounded-xl py-4 pl-12 pr-4 text-foreground placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all disabled:opacity-50"
          />
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground/70" />
        </div>
      </div>

      <div className="space-y-3">
        <label className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
          Target Channels
        </label>
        <div className="flex flex-wrap gap-3">
          {platforms.map((platform) => {
            const isSelected = selectedPlatforms.includes(platform);
            return (
              <button
                key={platform}
                type="button"
                disabled={isLoading}
                onClick={() => handlePlatformToggle(platform)}
                className={`px-4 py-2.5 rounded-xl border text-sm font-medium transition-all duration-200 cursor-pointer disabled:opacity-50 ${
                  isSelected
                    ? "bg-primary text-white border-primary shadow-lg shadow-primary/20"
                    : "bg-[#0d131f] text-muted-foreground border-card-border hover:bg-white/5 hover:text-foreground"
                }`}
              >
                {platform}
              </button>
            );
          })}
        </div>
      </div>

      <button
        type="submit"
        disabled={isLoading || !prompt.trim()}
        className="w-full py-4 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary-hover hover:to-indigo-700 text-white font-bold rounded-xl transition-all duration-300 shadow-xl shadow-primary/10 flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
      >
        {isLoading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            <span>Discovering Influencers...</span>
          </>
        ) : (
          <>
            <Search className="h-5 w-5" />
            <span>Discover Profiles</span>
          </>
        )}
      </button>
    </form>
  );
}
