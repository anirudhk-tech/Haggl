"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
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
        <div className="p-6 text-center">
          <p className="text-muted-foreground">Vendor not found</p>
          <Button asChild variant="link" className="mt-2">
            <Link href="/vendors">Back to vendors</Link>
          </Button>
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

  return (
    <>
      <Header title={vendor.vendor_name} />
      <div className="p-6 space-y-6 animate-fade-in">
        {/* Back Link (Desktop) */}
        <div className="hidden md:block">
          <Button asChild variant="ghost" size="sm" className="-ml-2">
            <Link href="/vendors">
              <ArrowLeft className="h-4 w-4 mr-1" />
              Back to vendors
            </Link>
          </Button>
        </div>

        {/* Vendor Header */}
        <div className="flex flex-col md:flex-row gap-6">
          {/* Radar Chart */}
          <Card className="md:w-80">
            <CardContent className="pt-6">
              <VendorRadarChart scores={vendor.scores} size="lg" />
              <div className="text-center mt-4">
                <span className="text-3xl font-semibold text-primary">
                  {finalScore.toFixed(1)}
                </span>
                <p className="text-sm text-muted-foreground">Final Score</p>
              </div>
            </CardContent>
          </Card>

          {/* Vendor Info */}
          <div className="flex-1 space-y-4">
            <div>
              <h1 className="text-2xl font-semibold">{vendor.vendor_name}</h1>
              <div className="flex flex-wrap gap-2 mt-2">
                {vendor.certifications.map((cert) => (
                  <Badge key={cert} variant="secondary">
                    {cert}
                  </Badge>
                ))}
              </div>
            </div>

            {/* Contact Info */}
            <Card>
              <CardContent className="p-4 space-y-3">
                {vendor.phone && (
                  <div className="flex items-center gap-3 text-sm">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <span>{vendor.phone}</span>
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
                        <span className="text-muted-foreground">
                          {" "}
                          ({vendor.distance_miles.toFixed(1)} mi)
                        </span>
                      )}
                    </span>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Products */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm flex items-center gap-2">
                  <Package className="h-4 w-4" />
                  Products
                </CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="flex flex-wrap gap-2">
                  {vendor.products.map((product) => (
                    <Badge key={product} variant="outline">
                      {product}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        <Separator />

        {/* Preference Learning */}
        <div className="grid md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Adjust Preferences</CardTitle>
            </CardHeader>
            <CardContent>
              <PreferenceControls
                weights={weights}
                onUpdate={handleWeightUpdate}
              />
              <p className="text-xs text-muted-foreground mt-4">
                Your preferences affect how all vendors are ranked.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Score Breakdown</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Quality</span>
                <span className="font-medium">{vendor.scores.quality}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Affordability</span>
                <span className="font-medium">{vendor.scores.affordability}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Shipping</span>
                <span className="font-medium">{vendor.scores.shipping}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Reliability</span>
                <span className="font-medium">{vendor.scores.reliability}</span>
              </div>
              <Separator />
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Embedding Score</span>
                <span className="font-medium">{vendor.embedding_score.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Parameter Score</span>
                <span className="font-medium">{parameterScore.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-sm font-medium">
                <span>Final Score</span>
                <span className="text-primary">{finalScore.toFixed(1)}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Order History */}
        {vendorOrders.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Star className="h-4 w-4" />
                Order History
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {vendorOrders.map((order) => (
                  <Link
                    key={order.order_id}
                    href={`/order/${order.order_id}`}
                    className="flex items-center justify-between p-3 rounded-lg border hover:bg-secondary/30 transition-colors"
                  >
                    <div>
                      <p className="font-medium text-sm">#{order.order_id}</p>
                      <p className="text-xs text-muted-foreground">
                        {order.ingredients
                          .filter((i) => i.vendor_name === vendor.vendor_name)
                          .map((i) => `${i.quantity} ${i.unit} ${i.name}`)
                          .join(", ")}
                      </p>
                    </div>
                    <Badge variant="outline">{order.status}</Badge>
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="flex gap-3">
          <Button asChild className="flex-1">
            <Link href={`/order/new?vendor=${vendor.vendor_id}`}>
              Place Order
            </Link>
          </Button>
          <Button variant="outline" asChild>
            <a href={`tel:${vendor.phone}`}>
              <Phone className="h-4 w-4 mr-2" />
              Call
            </a>
          </Button>
        </div>
      </div>
    </>
  );
}
