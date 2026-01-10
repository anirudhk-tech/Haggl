"use client";

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
    <div className={compact ? "space-y-2" : "space-y-0"}>
      {PARAMS.map(({ key, label }) => (
        <div
          key={key}
          className="flex items-center justify-between py-3 border-b border-border last:border-0"
        >
          <span className="text-xs uppercase tracking-wider text-muted-foreground">
            {label}
          </span>
          <div className="flex items-center gap-2">
            <button
              className="fill-hover-vertical h-7 w-7 flex items-center justify-center border border-border"
              onClick={() => onUpdate(key, "up")}
              disabled={weights[key] >= 0.6}
            >
              <ChevronUp className="h-4 w-4 relative z-10" />
            </button>
            <span className="text-sm font-medium w-12 text-center font-mono">
              {Math.round(weights[key] * 100)}%
            </span>
            <button
              className="fill-hover-vertical h-7 w-7 flex items-center justify-center border border-border"
              onClick={() => onUpdate(key, "down")}
              disabled={weights[key] <= 0.05}
            >
              <ChevronDown className="h-4 w-4 relative z-10" />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
