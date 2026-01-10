"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
      <div className="p-6 space-y-6 animate-fade-in">
        {/* Page Title */}
        <div className="hidden md:flex md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Vendors</h1>
            <p className="text-muted-foreground text-sm mt-1">
              {vendors.length} vendors ranked by your preferences
            </p>
          </div>
        </div>

        {/* Search and Filter Bar */}
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search vendors or products..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9"
            />
          </div>
          <Button
            variant={showPreferences ? "default" : "outline"}
            size="icon"
            onClick={() => setShowPreferences(!showPreferences)}
          >
            <SlidersHorizontal className="h-4 w-4" />
          </Button>
        </div>

        {/* Preference Controls */}
        {showPreferences && (
          <Card className="animate-slide-up">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm">Your Preferences</CardTitle>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleReset}
                  className="h-7 text-xs"
                >
                  <RotateCcw className="h-3 w-3 mr-1" />
                  Reset
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <PreferenceControls
                weights={weights}
                onUpdate={handleWeightUpdate}
              />
              <p className="text-xs text-muted-foreground mt-4">
                Click arrows to adjust importance. Vendors re-rank in real-time.
              </p>
            </CardContent>
          </Card>
        )}

        {/* Vendor Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 stagger-children">
          {vendors.map((vendor) => (
            <VendorCard key={vendor.vendor_id} vendor={vendor} />
          ))}
        </div>

        {vendors.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground">No vendors found</p>
            <Button
              variant="link"
              onClick={() => setSearch("")}
              className="mt-2"
            >
              Clear search
            </Button>
          </div>
        )}
      </div>
    </>
  );
}
