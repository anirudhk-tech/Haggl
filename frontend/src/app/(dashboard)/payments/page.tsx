import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/layout/nav";
import { demoPayments, demoStats } from "@/lib/demo-data";
import { ExternalLink } from "lucide-react";

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
    year: "numeric",
  });
}

function getStatusColor(status: string) {
  switch (status) {
    case "executed":
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
    case "authorized":
      return "bg-blue-50 text-blue-700 border-blue-200";
    case "failed":
      return "bg-red-50 text-red-700 border-red-200";
    default:
      return "bg-gray-50 text-gray-700 border-gray-200";
  }
}

export default function PaymentsPage() {
  return (
    <>
      <Header title="Payments" />
      <div className="p-6 space-y-6 animate-fade-in">
        {/* Page Title */}
        <div className="hidden md:block">
          <h1 className="text-2xl font-semibold">Payments</h1>
          <p className="text-muted-foreground text-sm mt-1">
            Transaction history with x402 verification
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 stagger-children">
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground">This Month</p>
              <p className="text-xl font-semibold mt-1">
                {formatCurrency(demoStats.totalSpent)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground">Transactions</p>
              <p className="text-xl font-semibold mt-1">{demoPayments.length}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground">Avg. Order</p>
              <p className="text-xl font-semibold mt-1">
                {formatCurrency(demoStats.totalSpent / demoPayments.length)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4">
              <p className="text-xs text-muted-foreground">Savings</p>
              <p className="text-xl font-semibold text-emerald-600 mt-1">
                {formatCurrency(demoStats.monthlySavings)}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Transaction List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Transaction History</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            <div className="divide-y divide-border">
              {demoPayments.map((payment) => (
                <div
                  key={payment.invoice_id}
                  className="p-4 hover:bg-secondary/30 transition-colors"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-sm">
                          {payment.vendor_name}
                        </span>
                        <Badge
                          variant="outline"
                          className={getStatusColor(payment.status)}
                        >
                          {payment.status}
                        </Badge>
                      </div>
                      <p className="text-xs text-muted-foreground mt-1">
                        {formatDate(payment.date)} &middot; {payment.invoice_id}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{formatCurrency(payment.amount_usd)}</p>
                    </div>
                  </div>

                  {/* Transaction Details */}
                  <div className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                    {payment.x402_tx_hash && (
                      <a
                        href={`https://basescan.org/tx/${payment.x402_tx_hash}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-primary hover:underline"
                      >
                        x402: {payment.x402_tx_hash}
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    )}
                    {payment.ach_confirmation && (
                      <span>ACH: {payment.ach_confirmation}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </>
  );
}
