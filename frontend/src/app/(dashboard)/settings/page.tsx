"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Header } from "@/components/layout/nav";
import { PreferenceControls } from "@/components/vendors/preference-controls";
import { demoProfile, defaultWeights } from "@/lib/demo-data";
import type { PreferenceWeights } from "@/lib/types";
import { RotateCcw, Save } from "lucide-react";
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
      <div className="p-6 space-y-6 animate-fade-in max-w-2xl mx-auto">
        {/* Page Title */}
        <div className="hidden md:block">
          <h1 className="text-2xl font-semibold">Settings</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage your business profile and preferences
          </p>
        </div>

        {/* Business Profile */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Business Profile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm text-muted-foreground">Business Name</label>
              <Input
                value={profile.business_name}
                onChange={(e) =>
                  setProfile({ ...profile, business_name: e.target.value })
                }
                className="mt-1"
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-muted-foreground">City</label>
                <Input
                  value={profile.location.city}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      location: { ...profile.location, city: e.target.value },
                    })
                  }
                  className="mt-1"
                />
              </div>
              <div>
                <label className="text-sm text-muted-foreground">State</label>
                <Input
                  value={profile.location.state}
                  onChange={(e) =>
                    setProfile({
                      ...profile,
                      location: { ...profile.location, state: e.target.value },
                    })
                  }
                  className="mt-1"
                />
              </div>
            </div>
            <div>
              <label className="text-sm text-muted-foreground">Phone</label>
              <Input
                value={profile.phone}
                onChange={(e) =>
                  setProfile({ ...profile, phone: e.target.value })
                }
                className="mt-1"
              />
            </div>
          </CardContent>
        </Card>

        {/* Preference Weights */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="text-base">Vendor Preferences</CardTitle>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleResetWeights}
              className="h-8"
            >
              <RotateCcw className="h-3 w-3 mr-1" />
              Reset
            </Button>
          </CardHeader>
          <CardContent>
            <PreferenceControls weights={weights} onUpdate={handleWeightUpdate} />
            <p className="text-xs text-muted-foreground mt-4">
              These weights determine how vendors are ranked. Weights always sum to 100%.
            </p>
          </CardContent>
        </Card>

        {/* Budget Settings */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Budget Settings</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm text-muted-foreground">
                Default Order Budget
              </label>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-muted-foreground">$</span>
                <Input
                  type="number"
                  value={budget.defaultOrder}
                  onChange={(e) =>
                    setBudget({ ...budget, defaultOrder: e.target.value })
                  }
                  className="max-w-32"
                />
              </div>
            </div>
            <div>
              <label className="text-sm text-muted-foreground">
                Monthly Spending Limit
              </label>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-muted-foreground">$</span>
                <Input
                  type="number"
                  value={budget.monthlyLimit}
                  onChange={(e) =>
                    setBudget({ ...budget, monthlyLimit: e.target.value })
                  }
                  className="max-w-32"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <Separator />

        {/* Save Button */}
        <Button onClick={handleSave} className="w-full">
          <Save className="h-4 w-4 mr-2" />
          Save Settings
        </Button>

        {/* Data Management */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Data Management</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button variant="outline" className="w-full justify-start">
              Export Order History (CSV)
            </Button>
            <Button
              variant="outline"
              className="w-full justify-start text-destructive hover:text-destructive"
              onClick={() => {
                setWeights(defaultWeights);
                toast.success("Preference data cleared");
              }}
            >
              Clear Preference Learning Data
            </Button>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
