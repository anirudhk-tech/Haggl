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
    lg: { width: 280, height: 280, fontSize: 11 },
  };

  const { width, height, fontSize } = dimensions[size];

  return (
    <div style={{ width, height }} className="mx-auto">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: 5, right: 5, bottom: 5, left: 5 }}>
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
    </div>
  );
}
