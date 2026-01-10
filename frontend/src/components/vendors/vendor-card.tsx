"use client";

import { Badge } from "@/components/ui/badge";
import { VendorRadarChart } from "./radar-chart";
import type { Vendor } from "@/lib/types";
import Link from "next/link";
import { ArrowUpRight, MapPin, DollarSign } from "lucide-react";

interface VendorCardProps {
  vendor: Vendor;
  index: number;
  onChartClick?: (vendor: Vendor) => void;
}

export function VendorCard({ vendor, index, onChartClick }: VendorCardProps) {
  const handleChartClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onChartClick?.(vendor);
  };

  return (
    <Link
      href={`/vendors/${vendor.vendor_id}`}
      className="fill-hover flex items-center gap-6 px-6 py-5 border-b border-border cursor-pointer group"
    >
      {/* Index */}
      <span className="text-xs text-muted-foreground w-6 font-mono relative z-10">
        {String(index + 1).padStart(2, "0")}
      </span>

      {/* Radar Chart - Clickable for corrections */}
      <div
        className="flex-shrink-0 relative z-20"
        onClick={handleChartClick}
      >
        <VendorRadarChart
          scores={vendor.scores}
          size="sm"
          interactive={!!onChartClick}
        />
      </div>

      {/* Vendor Info */}
      <div className="flex-1 min-w-0 relative z-10">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="font-medium text-sm">
              {vendor.vendor_name}
            </h3>
            <div className="flex items-center gap-3 mt-1">
              {vendor.price_per_unit && (
                <span className="text-xs text-muted-foreground flex items-center gap-1 font-mono">
                  <DollarSign className="h-3 w-3" />
                  {vendor.price_per_unit.toFixed(2)}/{vendor.unit}
                </span>
              )}
              {vendor.distance_miles && (
                <span className="text-xs text-muted-foreground flex items-center gap-1 font-mono">
                  <MapPin className="h-3 w-3" />
                  {vendor.distance_miles.toFixed(1)} mi
                </span>
              )}
            </div>
          </div>
          <div className="text-right">
            <span className="text-2xl font-medium tracking-tight font-mono">
              {vendor.final_score.toFixed(1)}
            </span>
            <p className="text-[10px] text-muted-foreground uppercase tracking-wider">
              Rank #{vendor.rank}
            </p>
          </div>
        </div>

        {/* Products */}
        <p className="text-xs text-muted-foreground mt-2 truncate">
          {vendor.products.join(", ")}
        </p>

        {/* Certifications */}
        <div className="flex flex-wrap gap-1 mt-2">
          {vendor.certifications.slice(0, 3).map((cert) => (
            <Badge
              key={cert}
              variant="outline"
              className="text-[10px] uppercase tracking-wider border-border"
            >
              {cert}
            </Badge>
          ))}
        </div>
      </div>

      {/* Arrow */}
      <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity relative z-10" />
    </Link>
  );
}
