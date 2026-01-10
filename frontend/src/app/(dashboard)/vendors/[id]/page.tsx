"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/layout/nav";
import { VendorRadarChart } from "@/components/vendors/radar-chart";
import { CorrectionDialog } from "@/components/vendors/correction-dialog";
import { demoVendors, demoOrders, demoVendorOrders } from "@/lib/demo-data";
import {
  ArrowLeft,
  Phone,
  Mail,
  Globe,
  MapPin,
  Star,
  Package,
  ArrowUpRight,
  DollarSign,
  ChevronUp,
  ChevronDown,
} from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";

const PARAM_LABELS = {
  quality: "Quality",
  affordability: "Affordability",
  shipping: "Shipping",
  reliability: "Reliability",
} as const;

export default function VendorProfilePage() {
  const params = useParams();
  const vendorId = params.id as string;
  const vendor = demoVendors.find((v) => v.vendor_id === vendorId);
  const [correctionDialogOpen, setCorrectionDialogOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState<string | null>(null);

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

  // Find orders with this vendor
  const vendorOrders = demoOrders.filter((order) =>
    order.ingredients.some((ing) => ing.vendor_name === vendor.vendor_name)
  );

  // Get previous orders for this vendor
  const previousOrders = demoVendorOrders[vendor.vendor_id] || [];

  const handleCorrection = async (
    parameter: keyof typeof PARAM_LABELS,
    direction: "up" | "down"
  ) => {
    setIsSubmitting(`${parameter}-${direction}`);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));

    toast.success(
      `${PARAM_LABELS[parameter]} correction submitted: actual is ${direction === "up" ? "higher" : "lower"}`
    );

    setIsSubmitting(null);
  };

  const handleChartClick = () => {
    setCorrectionDialogOpen(true);
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
            <div
              className="cursor-pointer hover:opacity-80 transition-opacity"
              onClick={handleChartClick}
            >
              <VendorRadarChart scores={vendor.scores} size="lg" interactive />
            </div>
            <div className="text-center mt-6">
              <span className="text-5xl font-medium tracking-tight font-mono">
                {vendor.final_score.toFixed(1)}
              </span>
              <p className="text-xs text-muted-foreground uppercase tracking-wider mt-2">
                Final Score • Rank #{vendor.rank}
              </p>
            </div>
          </div>

          {/* Contact & Products */}
          <div className="md:col-span-2">
            {/* Pricing Info */}
            {vendor.price_per_unit && (
              <div className="px-8 py-6 border-b border-border bg-secondary/30">
                <div className="flex items-center gap-6">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-4 w-4 text-muted-foreground" />
                    <span className="text-2xl font-medium font-mono">
                      ${vendor.price_per_unit.toFixed(2)}
                    </span>
                    <span className="text-muted-foreground">/{vendor.unit}</span>
                  </div>
                  {vendor.min_order && (
                    <div className="text-sm text-muted-foreground">
                      Min order: <span className="font-mono">{vendor.min_order} {vendor.min_order_unit}</span>
                    </div>
                  )}
                  {vendor.distance_miles && (
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <MapPin className="h-3 w-3" />
                      <span className="font-mono">{vendor.distance_miles.toFixed(1)} mi</span>
                    </div>
                  )}
                </div>
              </div>
            )}

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
                    <span>{vendor.address}</span>
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

        {/* Score Corrections Section */}
        <div className="grid md:grid-cols-2 border-b border-border">
          {/* Score Breakdown with Corrections */}
          <div className="border-b md:border-b-0 md:border-r border-border">
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">Score Corrections</h2>
            </div>
            <div>
              {(Object.entries(PARAM_LABELS) as [keyof typeof PARAM_LABELS, string][]).map(
                ([key, label]) => (
                  <div
                    key={key}
                    className="flex items-center justify-between px-8 py-4 border-b border-border last:border-0"
                  >
                    <div className="flex items-center gap-4">
                      <span className="text-xs uppercase tracking-wider text-muted-foreground w-28">
                        {label}
                      </span>
                      <span className="font-mono text-lg font-medium">
                        {vendor.scores[key]}
                      </span>
                    </div>
                    <div className="flex items-center gap-1">
                      <button
                        className="fill-hover-vertical h-9 w-9 flex items-center justify-center border border-border disabled:opacity-50"
                        onClick={() => handleCorrection(key, "up")}
                        disabled={isSubmitting !== null}
                        title="Actual is higher than predicted"
                      >
                        <ChevronUp className="h-4 w-4 relative z-10" />
                      </button>
                      <button
                        className="fill-hover-vertical h-9 w-9 flex items-center justify-center border border-border disabled:opacity-50"
                        onClick={() => handleCorrection(key, "down")}
                        disabled={isSubmitting !== null}
                        title="Actual is lower than predicted"
                      >
                        <ChevronDown className="h-4 w-4 relative z-10" />
                      </button>
                    </div>
                  </div>
                )
              )}
            </div>
            <div className="px-8 py-3 bg-secondary/30">
              <p className="text-[10px] text-muted-foreground">
                Click up if actual is higher than shown, down if lower. Corrections improve model predictions.
              </p>
            </div>
          </div>

          {/* Previous Orders */}
          <div>
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">Previous Orders ({previousOrders.length})</h2>
            </div>
            {previousOrders.length > 0 ? (
              <div>
                {previousOrders.map((order) => (
                  <div
                    key={order.order_id}
                    className="px-8 py-4 border-b border-border last:border-0"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="text-xs font-mono text-muted-foreground">
                          {order.order_id}
                        </p>
                        <p className="text-sm mt-0.5">{order.items.join(", ")}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {order.quantity}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-mono font-medium">
                          ${order.total.toFixed(2)}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {new Date(order.date).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="px-8 py-8 text-center">
                <p className="text-sm text-muted-foreground">No previous orders</p>
              </div>
            )}
          </div>
        </div>

        {/* Order History from Main Orders */}
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

      {/* Correction Dialog */}
      <CorrectionDialog
        vendor={vendor}
        open={correctionDialogOpen}
        onOpenChange={setCorrectionDialogOpen}
        onCorrection={(vendorId, parameter, direction) => {
          console.log("Correction:", { vendorId, parameter, direction });
        }}
      />
    </>
  );
}
