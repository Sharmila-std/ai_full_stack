"use client";

import React, { useState, useEffect } from "react";
import Navigation from "@/components/Navigation";
import CRMTable from "@/components/CRMTable";
import { Influencer } from "@/types";
import { Users, AlertTriangle, Download } from "lucide-react";

export default function CRMPage() {
  const [influencers, setInfluencers] = useState<Influencer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const fetchCRMList = async () => {
    setIsLoading(true);
    setError("");
    try {
      const res = await fetch(`${apiBaseUrl}/api/crm`);
      if (!res.ok) {
        throw new Error("Failed to fetch saved CRM records.");
      }
      const data: Influencer[] = await res.json();
      setInfluencers(data);
    } catch (err: any) {
      console.error(err);
      setError("Could not load CRM directory database. Verify backend connection.");
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCRMList();
  }, []);

  const handleDeleteInfluencer = async (id: string): Promise<boolean> => {
    try {
      const res = await fetch(`${apiBaseUrl}/api/crm/${id}`, {
        method: "DELETE",
      });
      if (res.ok) {
        // Filter out locally
        setInfluencers((prev) => prev.filter((inf) => inf.id !== id));
        return true;
      }
      return false;
    } catch (err) {
      console.error("Delete error:", err);
      return false;
    }
  };

  const handleExportCSV = () => {
    window.location.href = `${apiBaseUrl}/api/crm/export`;
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navigation />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 md:px-12 py-8 space-y-8">
        {/* Header section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-card-border/60 pb-6">
          <div className="space-y-1">
            <h1 className="text-3xl font-extrabold flex items-center space-x-2.5">
              <Users className="h-8 w-8 text-primary" />
              <span>CRM Directory</span>
            </h1>
            <p className="text-muted-foreground text-sm">
              Manage saved target creator profiles, view match stats, and review evaluation notes.
            </p>
          </div>
          
          <div className="flex flex-wrap items-center gap-3 self-start md:self-auto">
            <button
              onClick={handleExportCSV}
              disabled={influencers.length === 0}
              className="px-4 py-2.5 bg-primary/20 hover:bg-primary border border-primary/30 hover:border-primary text-indigo-300 hover:text-white text-sm font-semibold rounded-xl flex items-center space-x-2 transition-all duration-300 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Download className="h-4 w-4" />
              <span>Export CSV</span>
            </button>
            <div className="bg-[#131a26] border border-card-border px-4 py-2.5 rounded-xl flex items-center space-x-2">
              <span className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Total Directory:</span>
              <span className="text-sm font-bold text-indigo-400">{influencers.length} Profiles</span>
            </div>
          </div>
        </div>

        {/* Error State */}
        {error && (
          <div className="p-4 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-medium rounded-xl flex items-center space-x-2.5">
            <AlertTriangle className="h-5 w-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Loading Skeleton */}
        {isLoading && (
          <div className="space-y-4">
            <div className="shimmer w-full h-12 rounded-xl" />
            <div className="shimmer w-full h-32 rounded-xl" />
            <div className="shimmer w-full h-24 rounded-xl" />
          </div>
        )}

        {/* CRM Content */}
        {!isLoading && (
          <CRMTable influencers={influencers} onDelete={handleDeleteInfluencer} />
        )}
      </main>
    </div>
  );
}
