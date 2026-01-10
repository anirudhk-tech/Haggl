"use client";

import { Button } from "@/components/ui/button";
import { ChevronUp, ChevronDown } from "lucide-react";
import type { PreferenceWeights } from "@/lib/types";

interface PreferenceControlsProps {
  weights: PreferenceWeights;
  onUpdate: (param: keyof PreferenceWeights, direction: "up" | "down") => void;
  compact?: boolean;
}

const PARAMS: { key: keyof PreferenceWeights; label: string }[] = [
  { key: "quality", label: "Quality" },
  { key: "affordability", label: "Affordability" },
  { key: "shipping", label: "Shipping" },
  { key: "reliability", label: "Reliability" },
];

export function PreferenceControls({ weights, onUpdate, compact = false }: PreferenceControlsProps) {
  return (
    <div className={compact ? "space-y-2" : "space-y-3"}>
      {PARAMS.map(({ key, label }) => (
        <div
          key={key}
          className="flex items-center justify-between gap-2"
        >
          <span className={`${compact ? "text-xs" : "text-sm"} text-muted-foreground min-w-20`}>
            {label}
          </span>
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 hover:bg-emerald-50 hover:text-emerald-600 active:scale-90 transition-transform"
              onClick={() => onUpdate(key, "up")}
              disabled={weights[key] >= 0.6}
            >
              <ChevronUp className="h-4 w-4" />
            </Button>
            <span className={`${compact ? "text-xs" : "text-sm"} font-medium w-10 text-center tabular-nums`}>
              {Math.round(weights[key] * 100)}%
            </span>
            <Button
              variant="ghost"
              size="sm"
              className="h-6 w-6 p-0 hover:bg-red-50 hover:text-red-600 active:scale-90 transition-transform"
              onClick={() => onUpdate(key, "down")}
              disabled={weights[key] <= 0.05}
            >
              <ChevronDown className="h-4 w-4" />
            </Button>
          </div>
        </div>
      ))}
    </div>
  );
}
