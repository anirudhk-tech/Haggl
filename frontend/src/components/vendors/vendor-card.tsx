"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { VendorRadarChart } from "./radar-chart";
import type { Vendor } from "@/lib/types";
import Link from "next/link";
import { MapPin } from "lucide-react";

interface VendorCardProps {
  vendor: Vendor;
}

export function VendorCard({ vendor }: VendorCardProps) {
  return (
    <Link href={`/vendors/${vendor.vendor_id}`}>
      <Card className="hover:border-gray-300 transition-colors cursor-pointer group">
        <CardContent className="p-4">
          <div className="flex gap-4">
            {/* Radar Chart */}
            <div className="flex-shrink-0">
              <VendorRadarChart scores={vendor.scores} size="sm" />
            </div>

            {/* Vendor Info */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-medium text-sm group-hover:text-primary transition-colors">
                    {vendor.vendor_name}
                  </h3>
                  {vendor.distance_miles && (
                    <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                      <MapPin className="h-3 w-3" />
                      {vendor.distance_miles.toFixed(1)} mi
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <span className="text-lg font-semibold text-primary">
                    {vendor.final_score.toFixed(1)}
                  </span>
                  <p className="text-xs text-muted-foreground">
                    #{vendor.rank}
                  </p>
                </div>
              </div>

              {/* Products */}
              <p className="text-xs text-muted-foreground mt-2 truncate">
                {vendor.products.join(", ")}
              </p>

              {/* Certifications */}
              <div className="flex flex-wrap gap-1 mt-2">
                {vendor.certifications.slice(0, 2).map((cert) => (
                  <Badge
                    key={cert}
                    variant="secondary"
                    className="text-[10px] px-1.5 py-0"
                  >
                    {cert}
                  </Badge>
                ))}
                {vendor.certifications.length > 2 && (
                  <Badge
                    variant="secondary"
                    className="text-[10px] px-1.5 py-0"
                  >
                    +{vendor.certifications.length - 2}
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
