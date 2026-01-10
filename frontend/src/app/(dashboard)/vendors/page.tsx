"use client";

import { useState, useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Header } from "@/components/layout/nav";
import { VendorCard } from "@/components/vendors/vendor-card";
import { PreferenceControls } from "@/components/vendors/preference-controls";
import { demoVendors, defaultWeights } from "@/lib/demo-data";
import type { PreferenceWeights, Vendor } from "@/lib/types";
import { Search, SlidersHorizontal, RotateCcw } from "lucide-react";
import { toast } from "sonner";

function recalculateScores(vendors: Vendor[], weights: PreferenceWeights): Vendor[] {
  return vendors.map((vendor) => {
    const parameterScore =
      weights.quality * (vendor.scores.quality / 100) +
      weights.affordability * (vendor.scores.affordability / 100) +
      weights.shipping * (vendor.scores.shipping / 100) +
      weights.reliability * (vendor.scores.reliability / 100);

    const finalScore = 0.3 * vendor.embedding_score + 0.7 * parameterScore;

    return {
      ...vendor,
      parameter_score: parameterScore,
      final_score: finalScore * 100,
    };
  }).sort((a, b) => b.final_score - a.final_score)
    .map((v, i) => ({ ...v, rank: i + 1 }));
}

function normalizeWeights(weights: PreferenceWeights): PreferenceWeights {
  const total = weights.quality + weights.affordability + weights.shipping + weights.reliability;
  return {
    quality: weights.quality / total,
    affordability: weights.affordability / total,
    shipping: weights.shipping / total,
    reliability: weights.reliability / total,
  };
}

export default function VendorsPage() {
  const [search, setSearch] = useState("");
  const [weights, setWeights] = useState<PreferenceWeights>(defaultWeights);
  const [showPreferences, setShowPreferences] = useState(false);

  const vendors = useMemo(() => {
    let filtered = demoVendors;
    if (search) {
      const lower = search.toLowerCase();
      filtered = demoVendors.filter(
        (v) =>
          v.vendor_name.toLowerCase().includes(lower) ||
          v.products.some((p) => p.toLowerCase().includes(lower))
      );
    }
    return recalculateScores(filtered, weights);
  }, [search, weights]);

  const handleWeightUpdate = (param: keyof PreferenceWeights, direction: "up" | "down") => {
    setWeights((prev) => {
      const delta = direction === "up" ? 0.05 : -0.05;
      const newValue = Math.max(0.05, Math.min(0.6, prev[param] + delta));

      const updated = { ...prev, [param]: newValue };
      const normalized = normalizeWeights(updated);

      toast.success(
        `${param.charAt(0).toUpperCase() + param.slice(1)} ${direction === "up" ? "increased" : "decreased"} to ${Math.round(normalized[param] * 100)}%`
      );

      return normalized;
    });
  };

  const handleReset = () => {
    setWeights(defaultWeights);
    toast.success("Preferences reset to defaults");
  };

  return (
    <>
      <Header title="Vendors" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Vendors</h1>
          <p className="page-header-subtitle mt-1">
            {vendors.length} vendors ranked by your preferences
          </p>
        </header>

        {/* Search and Filter Bar */}
        <div className="flex border-b border-border">
          <div className="flex-1 flex items-center gap-3 px-6 py-3 border-r border-border">
            <Search className="h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search vendors or products..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="flex-1 bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none"
            />
          </div>
          <button
            className={`fill-hover px-6 py-3 flex items-center gap-2 text-sm font-medium uppercase tracking-wider ${showPreferences ? 'filled' : ''}`}
            onClick={() => setShowPreferences(!showPreferences)}
          >
            <SlidersHorizontal className="h-4 w-4 relative z-10" />
            <span className="relative z-10">Preferences</span>
          </button>
        </div>

        {/* Preference Controls */}
        {showPreferences && (
          <div className="border-b border-border animate-slide-up">
            <div className="px-8 py-4 border-b border-border flex items-center justify-between">
              <h2 className="section-header">Your Preferences</h2>
              <button
                className="fill-hover px-3 py-1.5 text-xs uppercase tracking-wider flex items-center gap-1 border border-border"
                onClick={handleReset}
              >
                <RotateCcw className="h-3 w-3 relative z-10" />
                <span className="relative z-10">Reset</span>
              </button>
            </div>
            <div className="px-8 py-4">
              <PreferenceControls
                weights={weights}
                onUpdate={handleWeightUpdate}
              />
              <p className="text-xs text-muted-foreground mt-4">
                Click arrows to adjust importance. Vendors re-rank in real-time.
              </p>
            </div>
          </div>
        )}

        {/* Vendor List */}
        <div className="stagger-children">
          {vendors.map((vendor, index) => (
            <VendorCard key={vendor.vendor_id} vendor={vendor} index={index} />
          ))}
        </div>

        {vendors.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted-foreground text-sm">No vendors found</p>
            <button
              className="fill-hover mt-4 px-4 py-2 text-sm border border-border"
              onClick={() => setSearch("")}
            >
              <span className="relative z-10">Clear search</span>
            </button>
          </div>
        )}
      </div>
    </>
  );
}
