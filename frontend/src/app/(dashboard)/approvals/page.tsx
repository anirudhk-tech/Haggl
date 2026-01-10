"use client";

import { useState } from "react";
import { Header } from "@/components/layout/nav";
import { Badge } from "@/components/ui/badge";
import { VendorRadarChart } from "@/components/vendors/radar-chart";
import { demoPendingApprovals } from "@/lib/demo-data";
import type { PendingApproval, Vendor } from "@/lib/types";
import { Check, X, MapPin, DollarSign, Mail, CreditCard, ChevronRight } from "lucide-react";
import { toast } from "sonner";

function formatDate(timestamp: string) {
  return new Date(timestamp).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<PendingApproval[]>(demoPendingApprovals);
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [showAlternative, setShowAlternative] = useState<Record<string, Vendor | null>>({});

  const handleApprove = async (approval: PendingApproval) => {
    setProcessingId(approval.approval_id);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 800));

    if (approval.has_invoice) {
      // Launch x402 process
      toast.success(
        `x402 payment initiated for ${formatCurrency(approval.total_price)} to ${approval.vendor.vendor_name}`,
        {
          description: "Transaction processing...",
        }
      );
    } else {
      // Send email requesting invoice
      toast.success(
        `Invoice request sent to ${approval.vendor.vendor_name}`,
        {
          description: `Email sent to ${approval.vendor.email}`,
        }
      );
    }

    // Remove from list
    setApprovals((prev) => prev.filter((a) => a.approval_id !== approval.approval_id));
    setProcessingId(null);
  };

  const handleDeny = async (approval: PendingApproval) => {
    setProcessingId(approval.approval_id);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 500));

    if (approval.alternatives.length > 0) {
      // Show next best alternative
      setShowAlternative((prev) => ({
        ...prev,
        [approval.approval_id]: approval.alternatives[0],
      }));
      toast.info("Showing next best vendor option");
    } else {
      // No alternatives, remove from list
      toast.error(`No alternative vendors for ${approval.ingredient}`);
      setApprovals((prev) => prev.filter((a) => a.approval_id !== approval.approval_id));
    }

    setProcessingId(null);
  };

  const handleSelectAlternative = async (approval: PendingApproval, alternative: Vendor) => {
    setProcessingId(approval.approval_id);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 800));

    const newPrice = alternative.price_per_unit! * approval.quantity;

    toast.success(
      `Switched to ${alternative.vendor_name}`,
      {
        description: `New order: ${approval.quantity} ${approval.unit} for ${formatCurrency(newPrice)}`,
      }
    );

    // Remove from list (in production, this would update the order)
    setApprovals((prev) => prev.filter((a) => a.approval_id !== approval.approval_id));
    setShowAlternative((prev) => ({ ...prev, [approval.approval_id]: null }));
    setProcessingId(null);
  };

  const handleCancelAlternative = (approvalId: string) => {
    setApprovals((prev) => prev.filter((a) => a.approval_id !== approvalId));
    setShowAlternative((prev) => ({ ...prev, [approvalId]: null }));
  };

  return (
    <>
      <Header title="Approvals" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Approvals</h1>
          <p className="page-header-subtitle mt-1">
            {approvals.length} pending approval{approvals.length !== 1 ? "s" : ""}
          </p>
        </header>

        {/* Approvals List */}
        <div className="stagger-children">
          {approvals.map((approval) => {
            const alternative = showAlternative[approval.approval_id];
            const displayVendor = alternative || approval.vendor;
            const displayPrice = alternative
              ? alternative.price_per_unit! * approval.quantity
              : approval.total_price;

            return (
              <div
                key={approval.approval_id}
                className="border-b border-border"
              >
                {/* Approval Header */}
                <div className="px-6 py-4 bg-secondary/30 flex items-center justify-between">
                  <div>
                    <h2 className="text-sm font-medium">
                      {approval.ingredient}
                    </h2>
                    <p className="text-xs text-muted-foreground font-mono mt-0.5">
                      {approval.quantity} {approval.unit} • {formatDate(approval.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {alternative && (
                      <Badge variant="outline" className="text-[10px] uppercase tracking-wider">
                        Alternative
                      </Badge>
                    )}
                    {!alternative && approval.has_invoice ? (
                      <Badge variant="outline" className="text-[10px] uppercase tracking-wider border-green-500/50 text-green-600">
                        Invoice Ready
                      </Badge>
                    ) : !alternative ? (
                      <Badge variant="outline" className="text-[10px] uppercase tracking-wider border-yellow-500/50 text-yellow-600">
                        No Invoice
                      </Badge>
                    ) : null}
                  </div>
                </div>

                {/* Vendor Card */}
                <div className="px-6 py-5">
                  <div className="flex items-start gap-6">
                    {/* Radar Chart */}
                    <div className="flex-shrink-0">
                      <VendorRadarChart scores={displayVendor.scores} size="sm" />
                    </div>

                    {/* Vendor Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div>
                          <h3 className="font-medium text-sm">
                            {displayVendor.vendor_name}
                          </h3>
                          <div className="flex items-center gap-3 mt-1">
                            {displayVendor.price_per_unit && (
                              <span className="text-xs text-muted-foreground flex items-center gap-1 font-mono">
                                <DollarSign className="h-3 w-3" />
                                {displayVendor.price_per_unit.toFixed(2)}/{displayVendor.unit}
                              </span>
                            )}
                            {displayVendor.distance_miles && (
                              <span className="text-xs text-muted-foreground flex items-center gap-1 font-mono">
                                <MapPin className="h-3 w-3" />
                                {displayVendor.distance_miles.toFixed(1)} mi
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="text-2xl font-medium tracking-tight font-mono">
                            {formatCurrency(displayPrice)}
                          </span>
                          <p className="text-[10px] text-muted-foreground uppercase tracking-wider">
                            Total
                          </p>
                        </div>
                      </div>

                      {/* Certifications */}
                      <div className="flex flex-wrap gap-1 mt-3">
                        {displayVendor.certifications.slice(0, 3).map((cert) => (
                          <Badge
                            key={cert}
                            variant="outline"
                            className="text-[10px] uppercase tracking-wider border-border"
                          >
                            {cert}
                          </Badge>
                        ))}
                      </div>

                      {/* Score Summary */}
                      <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                        <span>Quality: <span className="font-mono font-medium text-foreground">{displayVendor.scores.quality}</span></span>
                        <span>Afford: <span className="font-mono font-medium text-foreground">{displayVendor.scores.affordability}</span></span>
                        <span>Ship: <span className="font-mono font-medium text-foreground">{displayVendor.scores.shipping}</span></span>
                        <span>Reliable: <span className="font-mono font-medium text-foreground">{displayVendor.scores.reliability}</span></span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center gap-3 mt-5 pt-4 border-t border-border">
                    {alternative ? (
                      <>
                        <button
                          className="fill-hover flex-1 h-10 flex items-center justify-center gap-2 border border-border disabled:opacity-50"
                          onClick={() => handleSelectAlternative(approval, alternative)}
                          disabled={processingId === approval.approval_id}
                        >
                          <Check className="h-4 w-4 relative z-10" />
                          <span className="text-sm relative z-10">Select This Vendor</span>
                        </button>
                        <button
                          className="fill-hover h-10 px-4 flex items-center justify-center border border-border disabled:opacity-50"
                          onClick={() => handleCancelAlternative(approval.approval_id)}
                          disabled={processingId === approval.approval_id}
                        >
                          <X className="h-4 w-4 relative z-10" />
                        </button>
                      </>
                    ) : (
                      <>
                        <button
                          className="fill-hover flex-1 h-10 flex items-center justify-center gap-2 border border-foreground bg-foreground text-background disabled:opacity-50"
                          onClick={() => handleApprove(approval)}
                          disabled={processingId === approval.approval_id}
                        >
                          {approval.has_invoice ? (
                            <>
                              <CreditCard className="h-4 w-4 relative z-10" />
                              <span className="text-sm relative z-10">Approve & Pay (x402)</span>
                            </>
                          ) : (
                            <>
                              <Mail className="h-4 w-4 relative z-10" />
                              <span className="text-sm relative z-10">Approve & Request Invoice</span>
                            </>
                          )}
                        </button>
                        <button
                          className="fill-hover h-10 px-4 flex items-center justify-center gap-2 border border-border disabled:opacity-50"
                          onClick={() => handleDeny(approval)}
                          disabled={processingId === approval.approval_id}
                        >
                          <X className="h-4 w-4 relative z-10" />
                          <span className="text-sm relative z-10">Deny</span>
                          {approval.alternatives.length > 0 && (
                            <ChevronRight className="h-3 w-3 relative z-10 text-muted-foreground" />
                          )}
                        </button>
                      </>
                    )}
                  </div>

                  {/* Alternative hint */}
                  {!alternative && approval.alternatives.length > 0 && (
                    <p className="text-[10px] text-muted-foreground mt-2 text-center">
                      {approval.alternatives.length} alternative vendor{approval.alternatives.length > 1 ? "s" : ""} available
                    </p>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        {approvals.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted-foreground text-sm">No pending approvals</p>
            <p className="text-xs text-muted-foreground mt-1">
              New orders will appear here for your approval
            </p>
          </div>
        )}
      </div>
    </>
  );
}
