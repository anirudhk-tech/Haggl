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
}

export function VendorRadarChart({ scores, size = "md" }: VendorRadarChartProps) {
  const data = [
    { parameter: "Quality", value: scores.quality, fullMark: 100 },
    { parameter: "Afford.", value: scores.affordability, fullMark: 100 },
    { parameter: "Shipping", value: scores.shipping, fullMark: 100 },
    { parameter: "Reliable", value: scores.reliability, fullMark: 100 },
  ];

  const dimensions = {
    sm: { width: 120, height: 120, fontSize: 9 },
    md: { width: 180, height: 180, fontSize: 10 },
    lg: { width: 280, height: 280, fontSize: 12 },
  };

  const { width, height, fontSize } = dimensions[size];

  return (
    <div style={{ width, height }} className="mx-auto">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
          <PolarGrid stroke="#E5E7EB" />
          <PolarAngleAxis
            dataKey="parameter"
            tick={{ fontSize, fill: "#6B7280" }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={{ fontSize: fontSize - 2, fill: "#9CA3AF" }}
            tickCount={3}
          />
          <Radar
            name="Scores"
            dataKey="value"
            stroke="#2563EB"
            fill="#2563EB"
            fillOpacity={0.15}
            strokeWidth={2}
            animationDuration={600}
            animationEasing="ease-out"
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
