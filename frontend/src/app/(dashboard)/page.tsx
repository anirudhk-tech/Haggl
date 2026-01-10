import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/layout/nav";
import { demoOrders, demoStats } from "@/lib/demo-data";
import { ArrowUpRight, RotateCcw } from "lucide-react";
import Link from "next/link";

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(amount);
}

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function getStatusColor(status: string) {
  switch (status) {
    case "sourcing":
    case "calling":
      return "border-warning text-warning";
    case "confirmed":
    case "payment_pending":
    case "payment_processing":
      return "border-foreground text-foreground";
    case "paid":
    case "delivered":
      return "border-success text-success";
    case "failed":
      return "border-destructive text-destructive";
    default:
      return "border-muted-foreground text-muted-foreground";
  }
}

function getStatusLabel(status: string) {
  return status.split("_").map(word =>
    word.charAt(0).toUpperCase() + word.slice(1)
  ).join(" ");
}

export default function DashboardPage() {
  return (
    <>
      <Header />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Dashboard</h1>
          <p className="page-header-subtitle mt-1">
            Overview of your procurement activity
          </p>
        </header>

        {/* Stats Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 border-b border-border">
          <div className="px-8 py-6 border-b md:border-b-0 md:border-r border-border">
            <p className="section-header">Active Orders</p>
            <p className="text-4xl font-medium tracking-tight mt-2 mono-number">
              {String(demoStats.activeOrders).padStart(2, "0")}
            </p>
            <p className="text-xs text-muted-foreground mt-1">In progress</p>
          </div>

          <div className="px-8 py-6 border-b md:border-b-0 md:border-r border-border">
            <p className="section-header">Monthly Savings</p>
            <p className="text-4xl font-medium tracking-tight mt-2 mono-number text-success">
              {formatCurrency(demoStats.monthlySavings)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">Compared to market avg</p>
          </div>

          <div className="px-8 py-6">
            <p className="section-header">Pending Approval</p>
            <p className="text-4xl font-medium tracking-tight mt-2 mono-number">
              {String(demoStats.pendingApprovals).padStart(2, "0")}
            </p>
            <p className="text-xs text-muted-foreground mt-1">No action required</p>
          </div>
        </div>

        {/* Recent Orders */}
        <div>
          <div className="px-8 py-4 border-b border-border">
            <h2 className="section-header">Recent Orders</h2>
          </div>

          <div className="stagger-children">
            {demoOrders.map((order, index) => (
              <Link
                key={order.order_id}
                href={`/order/${order.order_id}`}
                className="fill-hover flex items-center justify-between px-8 py-5 border-b border-border cursor-pointer group"
              >
                <div className="flex items-center gap-6 relative z-10">
                  <span className="text-xs text-muted-foreground w-6 font-mono">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <div>
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-sm">
                        #{order.order_id}
                      </span>
                      <Badge
                        variant="outline"
                        className={getStatusColor(order.status)}
                      >
                        {getStatusLabel(order.status)}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {order.ingredients.map(i => i.name).join(", ")}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5 font-mono">
                      {formatDate(order.created_at)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-6 relative z-10">
                  <div className="text-right">
                    <p className="font-medium text-sm mono-number">
                      {formatCurrency(order.total_amount)}
                    </p>
                    {order.savings && order.savings > 0 && (
                      <p className="text-xs text-success mono-number">
                        Saved {formatCurrency(order.savings)}
                      </p>
                    )}
                  </div>
                  <ArrowUpRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* Quick Actions - Mobile */}
        <div className="md:hidden p-6 space-y-3 border-t border-border">
          <Link
            href="/order/new"
            className="fill-hover flex items-center justify-center h-12 border border-foreground text-sm font-medium uppercase tracking-wider"
          >
            <span className="relative z-10">New Order</span>
          </Link>
          <Link
            href="/vendors"
            className="fill-hover flex items-center justify-center h-12 border border-border text-sm font-medium uppercase tracking-wider"
          >
            <span className="relative z-10">Browse Vendors</span>
          </Link>
        </div>
      </div>
    </>
  );
}
