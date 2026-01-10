"use client";

import { useEffect, useState } from "react";
import { Header } from "@/components/layout/nav";
import { Badge } from "@/components/ui/badge";
import { LiveActivityFeed, StageProgress } from "@/components/activity/live-feed";
import type { AgentEvent, AgentStage, PendingApproval } from "@/lib/types";
import {
  CheckCircle2,
  Clock,
  Loader2,
  Package,
  DollarSign,
  Store,
} from "lucide-react";
import { toast } from "sonner";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

function ApprovalCard({
  approval,
  onApprove,
  isApproving,
}: {
  approval: PendingApproval;
  onApprove: () => void;
  isApproving: boolean;
}) {
  const totalPrice = approval.price * approval.quantity;

  return (
    <div className="border border-border animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-muted/30">
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="text-amber-500 border-amber-500">
            <Clock className="h-3 w-3 mr-1" />
            Pending
          </Badge>
          <span className="font-mono text-xs text-muted-foreground">
            {approval.order_id}
          </span>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {/* Product Info */}
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 border border-border flex items-center justify-center">
            <Package className="h-5 w-5 text-muted-foreground" />
          </div>
          <div>
            <p className="font-medium capitalize">{approval.product}</p>
            <p className="text-sm text-muted-foreground font-mono">
              {approval.quantity} {approval.unit}
            </p>
          </div>
        </div>

        {/* Vendor & Price */}
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center gap-2">
            <Store className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">
                Vendor
              </p>
              <p className="text-sm font-medium">{approval.vendor_name}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <DollarSign className="h-4 w-4 text-muted-foreground" />
            <div>
              <p className="text-xs text-muted-foreground uppercase tracking-wider">
                Total
              </p>
              <p className="text-sm font-medium font-mono">
                {formatCurrency(totalPrice)}
              </p>
            </div>
          </div>
        </div>

        {/* Price per unit */}
        <p className="text-xs text-muted-foreground">
          @ {formatCurrency(approval.price)}/{approval.unit}
        </p>
      </div>

      {/* Action */}
      <div className="px-4 py-3 border-t border-border">
        <button
          onClick={onApprove}
          disabled={isApproving}
          className="fill-hover w-full h-10 border border-emerald-500 text-emerald-500 text-sm font-medium uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-50"
        >
          {isApproving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin relative z-10" />
              <span className="relative z-10">Approving...</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="h-4 w-4 relative z-10" />
              <span className="relative z-10">Approve Order</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}

export default function OrdersPage() {
  const [pendingApprovals, setPendingApprovals] = useState<PendingApproval[]>([]);
  const [approvingIds, setApprovingIds] = useState<Set<string>>(new Set());
  const [currentStage, setCurrentStage] = useState<AgentStage>("idle");

  // Listen for SSE events for approval_required and update stage
  useEffect(() => {
    const eventSource = new EventSource(`${API_URL}/events/stream`);

    eventSource.onmessage = (e) => {
      try {
        const event: AgentEvent = JSON.parse(e.data);
        setCurrentStage(event.stage);

        // Add new approval when we get approval_required event
        if (event.event_type === "approval_required" && event.data) {
          const approval: PendingApproval = {
            order_id: event.order_id || `order-${Date.now()}`,
            vendor_name: event.data.vendor_name as string,
            price: event.data.price as number,
            product: event.data.product as string,
            quantity: event.data.quantity as number,
            unit: event.data.unit as string,
          };
          setPendingApprovals((prev) => {
            // Don't add duplicates
            if (prev.some((p) => p.order_id === approval.order_id)) {
              return prev;
            }
            return [approval, ...prev];
          });
        }

        // Remove approval when approved
        if (event.event_type === "order_update" && event.stage === "approved") {
          setPendingApprovals((prev) =>
            prev.filter((p) => p.order_id !== event.order_id)
          );
        }
      } catch (err) {
        console.error("Failed to parse event:", err);
      }
    };

    return () => eventSource.close();
  }, []);

  // Fetch pending approvals on mount
  useEffect(() => {
    fetch(`${API_URL}/orders/pending`)
      .then((res) => res.json())
      .then((data) => {
        if (data.orders) {
          setPendingApprovals(data.orders);
        }
      })
      .catch(console.error);
  }, []);

  const handleApprove = async (orderId: string) => {
    setApprovingIds((prev) => new Set([...prev, orderId]));

    try {
      const res = await fetch(`${API_URL}/orders/approve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ order_id: orderId }),
      });

      const data = await res.json();

      if (data.status === "approved") {
        toast.success("Order approved! 🎉", {
          description: data.message,
        });
        setPendingApprovals((prev) => prev.filter((p) => p.order_id !== orderId));
      } else {
        toast.error("Failed to approve order");
      }
    } catch (err) {
      toast.error("Failed to approve order");
      console.error(err);
    } finally {
      setApprovingIds((prev) => {
        const next = new Set(prev);
        next.delete(orderId);
        return next;
      });
    }
  };

  return (
    <>
      <Header title="Orders" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Orders & Activity</h1>
          <p className="page-header-subtitle mt-1">
            Real-time agent activity and pending approvals
          </p>
        </header>

        {/* Stage Progress */}
        <StageProgress currentStage={currentStage} />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 divide-y lg:divide-y-0 lg:divide-x divide-border">
          {/* Left: Pending Approvals */}
          <div>
            <div className="px-6 py-4 border-b border-border">
              <h2 className="section-header flex items-center gap-2">
                <Clock className="h-4 w-4" />
                Pending Approvals
                {pendingApprovals.length > 0 && (
                  <Badge className="bg-amber-500 text-background">
                    {pendingApprovals.length}
                  </Badge>
                )}
              </h2>
            </div>

            <div className="p-4 space-y-4 max-h-[600px] overflow-y-auto">
              {pendingApprovals.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <CheckCircle2 className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-sm text-muted-foreground">
                    No pending approvals
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Orders will appear here when ready
                  </p>
                </div>
              ) : (
                pendingApprovals.map((approval) => (
                  <ApprovalCard
                    key={approval.order_id}
                    approval={approval}
                    onApprove={() => handleApprove(approval.order_id)}
                    isApproving={approvingIds.has(approval.order_id)}
                  />
                ))
              )}
            </div>
          </div>

          {/* Right: Live Activity Feed */}
          <div>
            <div className="px-6 py-4 border-b border-border">
              <h2 className="section-header">Live Activity</h2>
            </div>
            <LiveActivityFeed />
          </div>
        </div>
      </div>
    </>
  );
}
