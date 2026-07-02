"use client";

import React from "react";
import { ExternalLink, Check, UserPlus, Flame } from "lucide-react";
import { Influencer } from "@/types";

interface ResultCardProps {
  influencer: Influencer;
  isSaved: boolean;
  onSaveClick: (influencer: Influencer) => void;
}

export default function ResultCard({ influencer, isSaved, onSaveClick }: ResultCardProps) {
  const getPlatformColor = (platform: string) => {
    switch (platform.toLowerCase()) {
      case "instagram":
        return "text-pink-400 bg-pink-500/10 border-pink-500/20";
      case "youtube":
        return "text-red-400 bg-red-500/10 border-red-500/20";
      case "tiktok":
        return "text-cyan-400 bg-cyan-500/10 border-cyan-500/20";
      case "twitter":
      case "x":
        return "text-sky-400 bg-sky-500/10 border-sky-500/20";
      default:
        return "text-gray-400 bg-gray-500/10 border-gray-500/20";
    }
  };

  return (
    <div className="w-full glass rounded-2xl p-6 flex flex-col justify-between border border-card-border hover:border-primary/30 transition-all duration-300 relative group overflow-hidden">
      {/* Background glow hover effect */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-2xl group-hover:bg-primary/10 transition-all duration-300" />
      
      <div className="space-y-4">
        {/* Header: Platform & Score */}
        <div className="flex justify-between items-start">
          <span className={`px-2.5 py-1 rounded-lg border text-xs font-semibold uppercase tracking-wider ${getPlatformColor(influencer.platform)}`}>
            {influencer.platform}
          </span>
          <div className="flex items-center space-x-1 text-amber-400 font-bold bg-amber-400/5 px-2.5 py-1 rounded-lg border border-amber-400/10">
            <Flame className="h-4 w-4" />
            <span>{influencer.match_score}%</span>
          </div>
        </div>

        {/* Profile Info */}
        <div>
          <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors flex items-center space-x-2">
            <span>{influencer.name}</span>
            <a
              href={influencer.profile_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground/60 hover:text-foreground inline-flex items-center transition-colors"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          </h3>
          <p className="text-sm text-muted-foreground">@{influencer.username}</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 py-2 border-y border-card-border/50">
          <div>
            <span className="text-xs text-muted-foreground/70 block uppercase tracking-wider">Followers</span>
            <span className="font-semibold text-foreground text-sm">{influencer.followers || "Not Available"}</span>
          </div>
          <div>
            <span className="text-xs text-muted-foreground/70 block uppercase tracking-wider">Handle URL</span>
            <a 
              href={influencer.profile_url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-xs font-medium text-indigo-400 hover:underline truncate block"
            >
              Link Profile
            </a>
          </div>
        </div>

        {/* Bio */}
        {influencer.bio && (
          <div className="space-y-1">
            <span className="text-xs text-muted-foreground/70 uppercase tracking-wider">Bio Snippet</span>
            <p className="text-sm text-muted-foreground/90 line-clamp-3 leading-relaxed">
              {influencer.bio}
            </p>
          </div>
        )}

        {/* Match Reason */}
        {influencer.match_reason && (
          <div className="bg-indigo-950/20 border border-indigo-900/30 rounded-xl p-3 space-y-1">
            <span className="text-xs text-indigo-300 font-semibold uppercase tracking-wider block">Match Evaluation</span>
            <p className="text-xs text-indigo-200/90 leading-relaxed">
              {influencer.match_reason}
            </p>
          </div>
        )}
      </div>

      {/* Save Action */}
      <div className="mt-6">
        {isSaved ? (
          <div className="w-full py-2.5 bg-green-500/10 border border-green-500/20 text-green-400 text-sm font-semibold rounded-xl flex items-center justify-center space-x-2">
            <Check className="h-4 w-4" />
            <span>Saved to CRM</span>
          </div>
        ) : (
          <button
            onClick={() => onSaveClick(influencer)}
            className="w-full py-2.5 bg-[#0d131f] border border-card-border hover:bg-primary hover:text-white hover:border-primary text-muted-foreground font-semibold text-sm rounded-xl transition-all duration-300 flex items-center justify-center space-x-2 cursor-pointer"
          >
            <UserPlus className="h-4 w-4" />
            <span>Add to CRM</span>
          </button>
        )}
      </div>
    </div>
  );
}
