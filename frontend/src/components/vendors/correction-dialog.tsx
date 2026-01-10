"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { VendorRadarChart } from "./radar-chart";
import { demoVendorOrders } from "@/lib/demo-data";
import type { Vendor } from "@/lib/types";
import { ChevronUp, ChevronDown, MapPin, DollarSign, Package } from "lucide-react";
import { toast } from "sonner";

interface CorrectionDialogProps {
  vendor: Vendor;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCorrection?: (vendorId: string, parameter: string, direction: "up" | "down") => void;
}

const PARAMETERS: { key: keyof typeof PARAM_LABELS; label: string }[] = [
  { key: "quality", label: "Quality" },
  { key: "affordability", label: "Affordability" },
  { key: "shipping", label: "Shipping" },
  { key: "reliability", label: "Reliability" },
];

const PARAM_LABELS = {
  quality: "Quality",
  affordability: "Affordability",
  shipping: "Shipping",
  reliability: "Reliability",
};

export function CorrectionDialog({
  vendor,
  open,
  onOpenChange,
  onCorrection,
}: CorrectionDialogProps) {
  const [isSubmitting, setIsSubmitting] = useState<string | null>(null);
  const vendorOrders = demoVendorOrders[vendor.vendor_id] || [];

  const handleCorrection = async (
    parameter: keyof typeof PARAM_LABELS,
    direction: "up" | "down"
  ) => {
    setIsSubmitting(`${parameter}-${direction}`);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));

    // Call the correction handler
    onCorrection?.(vendor.vendor_id, parameter, direction);

    toast.success(
      `${PARAM_LABELS[parameter]} correction submitted: actual is ${direction === "up" ? "higher" : "lower"}`
    );

    setIsSubmitting(null);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
    }).format(amount);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-lg font-medium">
            {vendor.vendor_name}
          </DialogTitle>
        </DialogHeader>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Left Column: Chart and Corrections */}
          <div>
            {/* Radar Chart */}
            <div className="border border-border p-4 mb-4">
              <VendorRadarChart scores={vendor.scores} size="lg" />
            </div>

            {/* Score Corrections */}
            <div className="border border-border">
              <div className="px-4 py-3 border-b border-border">
                <h3 className="text-xs uppercase tracking-wider text-muted-foreground">
                  Score Corrections
                </h3>
              </div>
              <div>
                {PARAMETERS.map(({ key, label }) => (
                  <div
                    key={key}
                    className="flex items-center justify-between px-4 py-3 border-b border-border last:border-0"
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-xs uppercase tracking-wider text-muted-foreground w-24">
                        {label}
                      </span>
                      <span className="font-mono text-sm font-medium">
                        {vendor.scores[key]}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        className="fill-hover-vertical h-8 w-8 flex items-center justify-center border border-border disabled:opacity-50"
                        onClick={() => handleCorrection(key, "up")}
                        disabled={isSubmitting !== null}
                        title="Actual is higher"
                      >
                        <ChevronUp className="h-4 w-4 relative z-10" />
                      </button>
                      <button
                        className="fill-hover-vertical h-8 w-8 flex items-center justify-center border border-border disabled:opacity-50"
                        onClick={() => handleCorrection(key, "down")}
                        disabled={isSubmitting !== null}
                        title="Actual is lower"
                      >
                        <ChevronDown className="h-4 w-4 relative z-10" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="px-4 py-2 bg-secondary/30">
                <p className="text-[10px] text-muted-foreground">
                  Click up if actual score is higher than predicted, down if lower.
                </p>
              </div>
            </div>
          </div>

          {/* Right Column: Vendor Info and Orders */}
          <div className="space-y-4">
            {/* Vendor Info */}
            <div className="border border-border">
              <div className="px-4 py-3 border-b border-border">
                <h3 className="text-xs uppercase tracking-wider text-muted-foreground">
                  Vendor Info
                </h3>
              </div>
              <div className="p-4 space-y-3">
                {vendor.price_per_unit && (
                  <div className="flex items-center gap-3">
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      <span className="font-mono font-medium">
                        ${vendor.price_per_unit.toFixed(2)}
                      </span>
                      <span className="text-muted-foreground">/{vendor.unit}</span>
                    </span>
                  </div>
                )}
                {vendor.min_order && (
                  <div className="flex items-center gap-3">
                    <Package className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">
                      Min order:{" "}
                      <span className="font-mono font-medium">
                        {vendor.min_order} {vendor.min_order_unit}
                      </span>
                    </span>
                  </div>
                )}
                {vendor.distance_miles && (
                  <div className="flex items-center gap-3">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-mono">
                      {vendor.distance_miles.toFixed(1)} mi
                    </span>
                  </div>
                )}
                <div className="pt-2">
                  <p className="text-xs text-muted-foreground mb-2">Products</p>
                  <p className="text-sm">{vendor.products.join(", ")}</p>
                </div>
              </div>
            </div>

            {/* Previous Orders */}
            <div className="border border-border">
              <div className="px-4 py-3 border-b border-border">
                <h3 className="text-xs uppercase tracking-wider text-muted-foreground">
                  Previous Orders ({vendorOrders.length})
                </h3>
              </div>
              {vendorOrders.length > 0 ? (
                <div>
                  {vendorOrders.map((order, index) => (
                    <div
                      key={order.order_id}
                      className="px-4 py-3 border-b border-border last:border-0"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-xs font-mono text-muted-foreground">
                            {order.order_id}
                          </p>
                          <p className="text-sm mt-0.5">
                            {order.items.join(", ")}
                          </p>
                          <p className="text-xs text-muted-foreground mt-0.5">
                            {order.quantity}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-mono font-medium">
                            {formatCurrency(order.total)}
                          </p>
                          <p className="text-xs text-muted-foreground">
                            {formatDate(order.date)}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="px-4 py-6 text-center">
                  <p className="text-sm text-muted-foreground">
                    No previous orders
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
