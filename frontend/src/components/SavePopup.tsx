"use client";

import React, { useState } from "react";
import { X, Tag, FileText, Loader2 } from "lucide-react";

interface SavePopupProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (tags: string, notes: string) => Promise<boolean>;
  influencerName: string;
}

export default function SavePopup({ isOpen, onClose, onConfirm, influencerName }: SavePopupProps) {
  const [tags, setTags] = useState("");
  const [notes, setNotes] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError("");
    try {
      const success = await onConfirm(tags.trim(), notes.trim());
      if (success) {
        setTags("");
        setNotes("");
        onClose();
      } else {
        setError("Failed to save. This profile might already exist in the CRM.");
      }
    } catch (err) {
      setError("An error occurred while saving to CRM.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm p-4 animate-fadeIn">
      <div className="w-full max-w-md bg-[#0b0f19] border border-card-border/80 rounded-2xl p-6 shadow-2xl space-y-6 relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          disabled={isSubmitting}
          className="absolute top-4 right-4 text-muted-foreground hover:text-foreground hover:bg-white/5 p-1.5 rounded-lg transition-colors cursor-pointer"
        >
          <X className="h-4.5 w-4.5" />
        </button>

        {/* Header */}
        <div className="space-y-1 pr-8">
          <h3 className="text-lg font-bold text-foreground truncate">
            Save Creator Profile
          </h3>
          <p className="text-xs text-muted-foreground truncate">
            Adding <span className="font-semibold text-primary">{influencerName}</span> to CRM
          </p>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold rounded-xl">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Tags */}
          <div className="space-y-1.5">
            <label htmlFor="popup-tags" className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider flex items-center space-x-1.5">
              <Tag className="h-3 w-3 text-indigo-400" />
              <span>Tags (comma-separated)</span>
            </label>
            <input
              id="popup-tags"
              type="text"
              disabled={isSubmitting}
              value={tags}
              onChange={(e) => setTags(e.target.value)}
              placeholder="e.g. parenting, mom-blogger, chennai"
              className="w-full bg-[#070a10] border border-card-border/60 rounded-xl py-2.5 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1.5 focus:ring-primary/50 focus:border-primary transition-all disabled:opacity-50"
            />
          </div>

          {/* Notes */}
          <div className="space-y-1.5">
            <label htmlFor="popup-notes" className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider flex items-center space-x-1.5">
              <FileText className="h-3 w-3 text-indigo-400" />
              <span>Personal Notes</span>
            </label>
            <textarea
              id="popup-notes"
              rows={3}
              disabled={isSubmitting}
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Add any specific context or follow-up details..."
              className="w-full bg-[#070a10] border border-card-border/60 rounded-xl py-2.5 px-3.5 text-sm text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:ring-1.5 focus:ring-primary/50 focus:border-primary transition-all disabled:opacity-50 resize-none"
            />
          </div>

          {/* Action Buttons */}
          <div className="flex space-x-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="flex-1 py-2.5 border border-card-border hover:bg-white/5 text-muted-foreground hover:text-foreground font-semibold text-sm rounded-xl transition-all cursor-pointer disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 py-2.5 bg-gradient-to-r from-primary to-indigo-600 hover:from-primary-hover hover:to-indigo-700 text-white font-bold text-sm rounded-xl transition-all shadow-lg shadow-primary/10 flex items-center justify-center space-x-2 disabled:opacity-50 cursor-pointer"
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Saving...</span>
                </>
              ) : (
                <span>Save Profile</span>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
