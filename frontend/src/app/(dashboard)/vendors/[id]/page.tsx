"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/layout/nav";
import { VendorRadarChart } from "@/components/vendors/radar-chart";
import { PreferenceControls } from "@/components/vendors/preference-controls";
import { demoVendors, defaultWeights, demoOrders } from "@/lib/demo-data";
import type { PreferenceWeights } from "@/lib/types";
import {
  ArrowLeft,
  Phone,
  Mail,
  Globe,
  MapPin,
  Star,
  Package,
  ArrowUpRight,
  RotateCcw,
} from "lucide-react";
import Link from "next/link";
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

export default function VendorProfilePage() {
  const params = useParams();
  const vendorId = params.id as string;
  const vendor = demoVendors.find((v) => v.vendor_id === vendorId);
  const [weights, setWeights] = useState<PreferenceWeights>(defaultWeights);

  if (!vendor) {
    return (
      <>
        <Header title="Vendor" />
        <div className="p-8 text-center">
          <p className="text-muted-foreground">Vendor not found</p>
          <Link
            href="/vendors"
            className="fill-hover inline-flex items-center mt-4 px-4 py-2 text-sm border border-border"
          >
            <span className="relative z-10">Back to vendors</span>
          </Link>
        </div>
      </>
    );
  }

  // Calculate updated scores based on current weights
  const parameterScore =
    weights.quality * (vendor.scores.quality / 100) +
    weights.affordability * (vendor.scores.affordability / 100) +
    weights.shipping * (vendor.scores.shipping / 100) +
    weights.reliability * (vendor.scores.reliability / 100);
  const finalScore = (0.3 * vendor.embedding_score + 0.7 * parameterScore) * 100;

  // Find orders with this vendor
  const vendorOrders = demoOrders.filter((order) =>
    order.ingredients.some((ing) => ing.vendor_name === vendor.vendor_name)
  );

  const handleWeightUpdate = (param: keyof PreferenceWeights, direction: "up" | "down") => {
    setWeights((prev) => {
      const delta = direction === "up" ? 0.05 : -0.05;
      const newValue = Math.max(0.05, Math.min(0.6, prev[param] + delta));
      const updated = { ...prev, [param]: newValue };
      const normalized = normalizeWeights(updated);

      toast.success(
        `${param.charAt(0).toUpperCase() + param.slice(1)} preference updated`
      );

      return normalized;
    });
  };

  const handleReset = () => {
    setWeights(defaultWeights);
    toast.success("Preferences reset to defaults");
  };

  return (
    <>
      <Header title={vendor.vendor_name} />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <Link
            href="/vendors"
            className="fill-hover inline-flex items-center gap-2 px-3 py-1.5 text-xs uppercase tracking-wider border border-border mb-6"
          >
            <ArrowLeft className="h-3 w-3 relative z-10" />
            <span className="relative z-10">Back</span>
          </Link>
          <h1 className="page-header">{vendor.vendor_name}</h1>
          <div className="flex flex-wrap gap-2 mt-3">
            {vendor.certifications.map((cert) => (
              <Badge
                key={cert}
                variant="outline"
                className="text-[10px] uppercase tracking-wider border-border"
              >
                {cert}
              </Badge>
            ))}
          </div>
        </header>

        {/* Main Content Grid */}
        <div className="grid md:grid-cols-3 border-b border-border">
          {/* Radar Chart Section */}
          <div className="md:col-span-1 px-8 py-8 border-b md:border-b-0 md:border-r border-border">
            <VendorRadarChart scores={vendor.scores} size="lg" />
            <div className="text-center mt-6">
              <span className="text-5xl font-medium tracking-tight font-mono">
                {finalScore.toFixed(1)}
              </span>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mt-2">
                Final Score
              </p>
            </div>
          </div>

          {/* Contact & Products */}
          <div className="md:col-span-2">
            {/* Contact Info */}
            <div className="px-8 py-6 border-b border-border">
              <h2 className="section-header mb-4">Contact</h2>
              <div className="space-y-3">
                {vendor.phone && (
                  <div className="flex items-center gap-3 text-sm">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span className="font-mono">{vendor.phone}</span>
                  </div>
                )}
                {vendor.email && (
                  <div className="flex items-center gap-3 text-sm">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <span>{vendor.email}</span>
                  </div>
                )}
                {vendor.website && (
                  <div className="flex items-center gap-3 text-sm">
                    <Globe className="h-4 w-4 text-muted-foreground" />
                    <span>{vendor.website}</span>
                  </div>
                )}
                {vendor.address && (
                  <div className="flex items-center gap-3 text-sm">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span>
                      {vendor.address}
                      {vendor.distance_miles && (
                        <span className="text-muted-foreground font-mono">
                          {" "}
                          ({vendor.distance_miles.toFixed(1)} mi)
                        </span>
                      )}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Products */}
            <div className="px-8 py-6">
              <h2 className="section-header flex items-center gap-2 mb-4">
                <Package className="h-4 w-4" />
                Products
              </h2>
              <div className="flex flex-wrap gap-2">
                {vendor.products.map((product) => (
                  <Badge
                    key={product}
                    variant="outline"
                    className="text-xs border-border"
                  >
                    {product}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Preference Learning Section */}
        <div className="grid md:grid-cols-2 border-b border-border">
          {/* Adjust Preferences */}
          <div className="border-b md:border-b-0 md:border-r border-border">
            <div className="px-8 py-4 border-b border-border flex items-center justify-between">
              <h2 className="section-header">Adjust Preferences</h2>
              <button
                className="fill-hover px-3 py-1.5 text-xs uppercase tracking-wider flex items-center gap-1 border border-border"
                onClick={handleReset}
              >
                <RotateCcw className="h-3 w-3 relative z-10" />
                <span className="relative z-10">Reset</span>
              </button>
            </div>
            <div className="px-8 py-6">
              <PreferenceControls
                weights={weights}
                onUpdate={handleWeightUpdate}
              />
              <p className="text-xs text-muted-foreground mt-4">
                Your preferences affect how all vendors are ranked.
              </p>
            </div>
          </div>

          {/* Score Breakdown */}
          <div>
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">Score Breakdown</h2>
            </div>
            <div className="px-8 py-6 space-y-3">
              <div className="flex justify-between text-sm py-2 border-b border-border">
                <span className="text-xs uppercase tracking-wider text-muted-foreground">Quality</span>
                <span className="font-mono">{vendor.scores.quality}</span>
              </div>
              <div className="flex justify-between text-sm py-2 border-b border-border">
                <span className="text-xs uppercase tracking-wider text-muted-foreground">Affordability</span>
                <span className="font-mono">{vendor.scores.affordability}</span>
              </div>
              <div className="flex justify-between text-sm py-2 border-b border-border">
                <span className="text-xs uppercase tracking-wider text-muted-foreground">Shipping</span>
                <span className="font-mono">{vendor.scores.shipping}</span>
              </div>
              <div className="flex justify-between text-sm py-2 border-b border-border">
                <span className="text-xs uppercase tracking-wider text-muted-foreground">Reliability</span>
                <span className="font-mono">{vendor.scores.reliability}</span>
              </div>
              <div className="flex justify-between text-sm py-2 border-b border-border">
                <span className="text-xs uppercase tracking-wider text-muted-foreground">Embedding Score</span>
                <span className="font-mono">{vendor.embedding_score.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm py-2 border-b border-border">
                <span className="text-xs uppercase tracking-wider text-muted-foreground">Parameter Score</span>
                <span className="font-mono">{parameterScore.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm py-2 font-medium">
                <span className="text-xs uppercase tracking-wider">Final Score</span>
                <span className="font-mono text-lg">{finalScore.toFixed(1)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Order History */}
        {vendorOrders.length > 0 && (
          <div className="border-b border-border">
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header flex items-center gap-2">
                <Star className="h-4 w-4" />
                Order History
              </h2>
            </div>
            <div className="stagger-children">
              {vendorOrders.map((order, index) => (
                <Link
                  key={order.order_id}
                  href={`/order/${order.order_id}`}
                  className="fill-hover flex items-center justify-between px-8 py-4 border-b border-border last:border-0 group"
                >
                  <div className="flex items-center gap-4 relative z-10">
                    <span className="text-xs text-muted-foreground w-6 font-mono">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <div>
                      <p className="font-medium text-sm font-mono">#{order.order_id}</p>
                      <p className="text-xs text-muted-foreground">
                        {order.ingredients
                          .filter((i) => i.vendor_name === vendor.vendor_name)
                          .map((i) => `${i.quantity} ${i.unit} ${i.name}`)
                          .join(", ")}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 relative z-10">
                    <Badge variant="outline" className="text-[10px] uppercase tracking-wider border-border">
                      {order.status}
                    </Badge>
                    <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex border-b border-border">
          <Link
            href={`/order/new?vendor=${vendor.vendor_id}`}
            className="fill-hover flex-1 flex items-center justify-center h-14 text-sm font-medium uppercase tracking-wider border-r border-border"
          >
            <span className="relative z-10">Place Order</span>
          </Link>
          <a
            href={`tel:${vendor.phone}`}
            className="fill-hover flex items-center justify-center h-14 px-8 text-sm font-medium uppercase tracking-wider gap-2"
          >
            <Phone className="h-4 w-4 relative z-10" />
            <span className="relative z-10">Call</span>
          </a>
        </div>
      </div>
    </>
  );
}
