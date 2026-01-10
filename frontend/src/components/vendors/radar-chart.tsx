"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import type { VendorScores } from "@/lib/types";

interface VendorRadarChartProps {
  scores: VendorScores;
  size?: "sm" | "md" | "lg";
  onClick?: () => void;
  interactive?: boolean;
}

export function VendorRadarChart({
  scores,
  size = "md",
  onClick,
  interactive = false,
}: VendorRadarChartProps) {
  // Use abbreviated labels for small size (cards), full labels for md/lg
  const labels = size === "sm"
    ? { quality: "Quality", affordability: "Afford.", shipping: "Ship.", reliability: "Reliable" }
    : { quality: "Quality", affordability: "Affordability", shipping: "Shipping", reliability: "Reliability" };

  const data = [
    { parameter: labels.quality, value: scores.quality, fullMark: 100 },
    { parameter: labels.affordability, value: scores.affordability, fullMark: 100 },
    { parameter: labels.shipping, value: scores.shipping, fullMark: 100 },
    { parameter: labels.reliability, value: scores.reliability, fullMark: 100 },
  ];

  const dimensions = {
    sm: { width: 160, height: 160, fontSize: 9, margin: 20 },
    md: { width: 280, height: 280, fontSize: 11, margin: 40 },
    lg: { width: 360, height: 360, fontSize: 12, margin: 50 },
  };

  const { width, height, fontSize, margin } = dimensions[size];

  return (
    <div
      style={{ width, height }}
      className={`mx-auto ${interactive ? 'cursor-pointer hover:opacity-80 transition-opacity' : ''}`}
      onClick={onClick}
    >
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: margin, right: margin + 20, bottom: margin, left: margin + 20 }}>
          <PolarGrid stroke="#E5E0D8" strokeWidth={1} />
          <PolarAngleAxis
            dataKey="parameter"
            tick={{ fontSize, fill: "#737373", fontFamily: "var(--font-ibm-plex-mono)" }}
            tickLine={false}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: fontSize - 1, fill: "#A3A3A3" }}
            tickCount={3}
            axisLine={false}
          />
          <Radar
            name="Scores"
            dataKey="value"
            stroke="#0A0A0B"
            fill="#0A0A0B"
            fillOpacity={0.1}
            strokeWidth={1.5}
            animationDuration={400}
            animationEasing="ease-out"
          />
        </RadarChart>
      </ResponsiveContainer>
      {interactive && (
        <p className="text-[10px] text-center text-muted-foreground mt-1 uppercase tracking-wider">
          Click to correct
        </p>
      )}
    </div>
  );
}
