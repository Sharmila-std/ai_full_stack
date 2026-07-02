"use client";

import React, { useState } from "react";
import { ExternalLink, Trash2, ShieldAlert, Flame } from "lucide-react";
import { Influencer } from "@/types";

interface CRMTableProps {
  influencers: Influencer[];
  onDelete: (id: string) => Promise<boolean>;
}

export default function CRMTable({ influencers, onDelete }: CRMTableProps) {
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDeleteClick = async (id: string) => {
    if (!confirm("Are you sure you want to remove this influencer from the CRM?")) {
      return;
    }
    setDeletingId(id);
    try {
      await onDelete(id);
    } catch (e) {
      console.error("Delete failed:", e);
    } finally {
      setDeletingId(null);
    }
  };

  const getPlatformClass = (platform: string) => {
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

  if (influencers.length === 0) {
    return (
      <div className="w-full glass rounded-2xl p-12 text-center border border-card-border flex flex-col items-center justify-center space-y-4">
        <ShieldAlert className="h-12 w-12 text-muted-foreground/60" />
        <div className="space-y-1">
          <h3 className="text-lg font-bold text-foreground">No Influencers Saved</h3>
          <p className="text-sm text-muted-foreground">
            Search for profiles and add them to your directory list database.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full glass border border-card-border rounded-2xl overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-card-border bg-[#0d131f]/70 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              <th className="py-4 px-6">Influencer Profile</th>
              <th className="py-4 px-6">Platform</th>
              <th className="py-4 px-6 text-center">Score</th>
              <th className="py-4 px-6">Followers</th>
              <th className="py-4 px-6">Tags</th>
              <th className="py-4 px-6">Notes</th>
              <th className="py-4 px-6">Evaluation Reason</th>
              <th className="py-4 px-6 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-card-border/55 text-sm">
            {influencers.map((inf) => (
              <tr key={inf.id} className="hover:bg-white/5 transition-colors">
                {/* Profile column */}
                <td className="py-4 px-6">
                  <div className="font-semibold text-foreground flex items-center space-x-1.5">
                    <span>{inf.name}</span>
                    <a
                      href={inf.profile_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-muted-foreground/60 hover:text-foreground transition-colors inline-block"
                    >
                      <ExternalLink className="h-3.5 w-3.5" />
                    </a>
                  </div>
                  <div className="text-xs text-muted-foreground">@{inf.username}</div>
                </td>

                {/* Platform column */}
                <td className="py-4 px-6">
                  <span className={`px-2.5 py-0.5 rounded-lg border text-xs font-semibold uppercase ${getPlatformClass(inf.platform)}`}>
                    {inf.platform}
                  </span>
                </td>

                {/* Score column */}
                <td className="py-4 px-6 text-center">
                  <div className="inline-flex items-center space-x-0.5 text-amber-400 font-bold bg-amber-400/5 px-2 py-0.5 rounded border border-amber-400/10 text-xs">
                    <Flame className="h-3.5 w-3.5" />
                    <span>{inf.match_score}%</span>
                  </div>
                </td>

                {/* Followers count */}
                <td className="py-4 px-6 font-medium text-foreground">{inf.followers || "Not Available"}</td>

                {/* Tags column */}
                <td className="py-4 px-6">
                  <div className="flex flex-wrap gap-1 max-w-[150px]">
                    {inf.tags ? (
                      inf.tags.split(",").map((tag, tagIdx) => (
                        <span
                          key={tagIdx}
                          className="px-2 py-0.5 bg-primary/10 border border-primary/20 text-indigo-300 text-[10px] font-semibold rounded-md"
                        >
                          {tag.trim()}
                        </span>
                      ))
                    ) : (
                      <span className="text-muted-foreground/35 text-xs">-</span>
                    )}
                  </div>
                </td>

                {/* Notes column */}
                <td className="py-4 px-6 text-muted-foreground max-w-[180px] truncate" title={inf.notes}>
                  {inf.notes || <span className="text-muted-foreground/35 text-xs">-</span>}
                </td>

                {/* Reason column */}
                <td className="py-4 px-6 text-muted-foreground max-w-xs truncate" title={inf.match_reason}>
                  {inf.match_reason || "No matching reasoning recorded."}
                </td>

                {/* Actions column */}
                <td className="py-4 px-6 text-right">
                  <button
                    disabled={deletingId === inf.id}
                    onClick={() => inf.id && handleDeleteClick(inf.id)}
                    className="p-2 text-muted-foreground hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-all cursor-pointer disabled:opacity-50 inline-flex items-center"
                    title="Remove Influencer"
                  >
                    <Trash2 className="h-4.5 w-4.5" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
