import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Header } from "@/components/layout/nav";
import { demoOrders, demoStats } from "@/lib/demo-data";
import { Package, TrendingUp, Clock, ChevronRight, RotateCcw } from "lucide-react";
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
      return "bg-amber-50 text-amber-700 border-amber-200";
    case "confirmed":
    case "payment_pending":
    case "payment_processing":
      return "bg-blue-50 text-blue-700 border-blue-200";
    case "paid":
    case "delivered":
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
    case "failed":
      return "bg-red-50 text-red-700 border-red-200";
    default:
      return "bg-gray-50 text-gray-700 border-gray-200";
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
      <div className="p-6 space-y-6 animate-fade-in">
        {/* Page Title */}
        <div className="hidden md:block">
          <h1 className="text-2xl font-semibold">Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Overview of your procurement activity
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 stagger-children">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Orders
              </CardTitle>
              <Package className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold">{demoStats.activeOrders}</div>
              <p className="text-xs text-muted-foreground mt-1">
                In progress
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Monthly Savings
              </CardTitle>
              <TrendingUp className="h-4 w-4 text-emerald-500" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold text-emerald-600">
                {formatCurrency(demoStats.monthlySavings)}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Compared to market avg
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Pending Approval
              </CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-semibold">{demoStats.pendingApprovals}</div>
              <p className="text-xs text-muted-foreground mt-1">
                No action required
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Recent Orders */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Orders</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border">
              {demoOrders.map((order) => (
                <div
                  key={order.order_id}
                  className="flex items-center justify-between p-4 hover:bg-secondary/30 transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
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
                    <p className="text-sm text-muted-foreground mt-1 truncate">
                      {order.ingredients.map(i => i.name).join(", ")}
                    </p>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {formatDate(order.created_at)}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 ml-4">
                    <div className="text-right">
                      <p className="font-medium text-sm">
                        {formatCurrency(order.total_amount)}
                      </p>
                      {order.savings && order.savings > 0 && (
                        <p className="text-xs text-emerald-600">
                          Saved {formatCurrency(order.savings)}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" asChild>
                        <Link href={`/order/${order.order_id}`}>
                          <ChevronRight className="h-4 w-4" />
                        </Link>
                      </Button>
                      {order.status === "delivered" && (
                        <Button variant="ghost" size="sm" asChild>
                          <Link href={`/order/new?reorder=${order.order_id}`}>
                            <RotateCcw className="h-4 w-4" />
                          </Link>
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions (Mobile) */}
        <div className="md:hidden space-y-3">
          <Button asChild className="w-full" size="lg">
            <Link href="/order/new">New Order</Link>
          </Button>
          <Button asChild variant="outline" className="w-full" size="lg">
            <Link href="/vendors">Browse Vendors</Link>
          </Button>
        </div>
      </div>
    </>
  );
}
