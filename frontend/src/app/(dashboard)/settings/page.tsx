"use client";

import { useState } from "react";
import { Header } from "@/components/layout/nav";
import { PreferenceControls } from "@/components/vendors/preference-controls";
import { demoProfile, defaultWeights } from "@/lib/demo-data";
import type { PreferenceWeights } from "@/lib/types";
import { RotateCcw, Save, Download, Trash2 } from "lucide-react";
import { toast } from "sonner";

function normalizeWeights(weights: PreferenceWeights): PreferenceWeights {
  const total = weights.quality + weights.affordability + weights.shipping + weights.reliability;
  return {
    quality: weights.quality / total,
    affordability: weights.affordability / total,
    shipping: weights.shipping / total,
    reliability: weights.reliability / total,
  };
}

export default function SettingsPage() {
  const [profile, setProfile] = useState(demoProfile);
  const [weights, setWeights] = useState<PreferenceWeights>(defaultWeights);
  const [budget, setBudget] = useState({
    defaultOrder: "2000",
    monthlyLimit: "10000",
  });

  const handleWeightUpdate = (param: keyof PreferenceWeights, direction: "up" | "down") => {
    setWeights((prev) => {
      const delta = direction === "up" ? 0.05 : -0.05;
      const newValue = Math.max(0.05, Math.min(0.6, prev[param] + delta));
      const updated = { ...prev, [param]: newValue };
      return normalizeWeights(updated);
    });
  };

  const handleResetWeights = () => {
    setWeights(defaultWeights);
    toast.success("Preferences reset to defaults");
  };

  const handleSave = () => {
    toast.success("Settings saved");
  };

  return (
    <>
      <Header title="Settings" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Settings</h1>
          <p className="page-header-subtitle mt-1">
            Manage your business profile and preferences
          </p>
        </header>

        {/* Business Profile */}
        <div className="border-b border-border">
          <div className="px-8 py-4 border-b border-border">
            <h2 className="section-header">Business Profile</h2>
          </div>
          <div className="px-8 py-6 space-y-4">
            <div>
              <label className="text-xs uppercase tracking-wider text-muted-foreground">
                Business Name
              </label>
              <input
                type="text"
                value={profile.business_name}
                onChange={(e) =>
                  setProfile({ ...profile, business_name: e.target.value })
                }
                className="w-full h-10 px-3 mt-2 bg-transparent border border-border text-sm focus:outline-none focus:border-foreground"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-xs uppercase tracking-wider text-muted-foreground">
                  City
                </label>
                <input
                  type="text"
                  value={profile.location.city}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      location: { ...profile.location, city: e.target.value },
                    })
                  }
                  className="w-full h-10 px-3 mt-2 bg-transparent border border-border text-sm focus:outline-none focus:border-foreground"
                />
              </div>
              <div>
                <label className="text-xs uppercase tracking-wider text-muted-foreground">
                  State
                </label>
                <input
                  type="text"
                  value={profile.location.state}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      location: { ...profile.location, state: e.target.value },
                    })
                  }
                  className="w-full h-10 px-3 mt-2 bg-transparent border border-border text-sm focus:outline-none focus:border-foreground"
                />
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-muted-foreground">
                Phone
              </label>
              <input
                type="text"
                value={profile.phone}
                onChange={(e) =>
                  setProfile({ ...profile, phone: e.target.value })
                }
                className="w-full h-10 px-3 mt-2 bg-transparent border border-border text-sm font-mono focus:outline-none focus:border-foreground"
              />
            </div>
          </div>
        </div>

        {/* Vendor Preferences */}
        <div className="border-b border-border">
          <div className="px-8 py-4 border-b border-border flex items-center justify-between">
            <h2 className="section-header">Vendor Preferences</h2>
            <button
              className="fill-hover px-3 py-1.5 text-xs uppercase tracking-wider flex items-center gap-1 border border-border"
              onClick={handleResetWeights}
            >
              <RotateCcw className="h-3 w-3 relative z-10" />
              <span className="relative z-10">Reset</span>
            </button>
          </div>
          <div className="px-8 py-6">
            <PreferenceControls weights={weights} onUpdate={handleWeightUpdate} />
            <p className="text-xs text-muted-foreground mt-4">
              These weights determine how vendors are ranked. Weights always sum to 100%.
            </p>
          </div>
        </div>

        {/* Budget Settings */}
        <div className="border-b border-border">
          <div className="px-8 py-4 border-b border-border">
            <h2 className="section-header">Budget Settings</h2>
          </div>
          <div className="px-8 py-6 space-y-4">
            <div>
              <label className="text-xs uppercase tracking-wider text-muted-foreground">
                Default Order Budget
              </label>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-muted-foreground">$</span>
                <input
                  type="number"
                  value={budget.defaultOrder}
                  onChange={(e) =>
                    setBudget({ ...budget, defaultOrder: e.target.value })
                  }
                  className="w-32 h-10 px-3 bg-transparent border border-border text-sm font-mono focus:outline-none focus:border-foreground"
                />
              </div>
            </div>
            <div>
              <label className="text-xs uppercase tracking-wider text-muted-foreground">
                Monthly Spending Limit
              </label>
              <div className="flex items-center gap-2 mt-2">
                <span className="text-muted-foreground">$</span>
                <input
                  type="number"
                  value={budget.monthlyLimit}
                  onChange={(e) =>
                    setBudget({ ...budget, monthlyLimit: e.target.value })
                  }
                  className="w-32 h-10 px-3 bg-transparent border border-border text-sm font-mono focus:outline-none focus:border-foreground"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Save Button */}
        <div className="border-b border-border">
          <button
            onClick={handleSave}
            className="fill-hover w-full h-14 flex items-center justify-center gap-2 text-sm font-medium uppercase tracking-wider"
          >
            <Save className="h-4 w-4 relative z-10" />
            <span className="relative z-10">Save Settings</span>
          </button>
        </div>

        {/* Data Management */}
        <div>
          <div className="px-8 py-4 border-b border-border">
            <h2 className="section-header">Data Management</h2>
          </div>
          <div className="stagger-children">
            <button className="fill-hover w-full flex items-center gap-3 px-8 py-4 border-b border-border text-sm text-left">
              <Download className="h-4 w-4 relative z-10" />
              <span className="relative z-10">Export Order History (CSV)</span>
            </button>
            <button
              className="fill-hover-destructive w-full flex items-center gap-3 px-8 py-4 border-b border-border text-sm text-left text-destructive"
              onClick={() => {
                setWeights(defaultWeights);
                toast.success("Preference data cleared");
              }}
            >
              <Trash2 className="h-4 w-4 relative z-10" />
              <span className="relative z-10">Clear Preference Learning Data</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
