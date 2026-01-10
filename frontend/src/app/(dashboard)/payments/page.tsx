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
      return "border-success text-success";
    case "authorized":
      return "border-foreground text-foreground";
    case "failed":
      return "border-destructive text-destructive";
    default:
      return "border-muted-foreground text-muted-foreground";
  }
}

export default function PaymentsPage() {
  return (
    <>
      <Header title="Payments" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Payments</h1>
          <p className="page-header-subtitle mt-1">
            Transaction history with x402 verification
          </p>
        </header>

        {/* Stats Row */}
        <div className="grid grid-cols-2 md:grid-cols-4 border-b border-border">
          <div className="px-6 py-6 border-r border-b md:border-b-0 border-border">
            <p className="section-header">This Month</p>
            <p className="text-2xl font-medium tracking-tight mt-2 mono-number">
              {formatCurrency(demoStats.totalSpent)}
            </p>
          </div>
          <div className="px-6 py-6 border-b md:border-b-0 md:border-r border-border">
            <p className="section-header">Transactions</p>
            <p className="text-2xl font-medium tracking-tight mt-2 mono-number">
              {String(demoPayments.length).padStart(2, "0")}
            </p>
          </div>
          <div className="px-6 py-6 border-r border-border">
            <p className="section-header">Avg. Order</p>
            <p className="text-2xl font-medium tracking-tight mt-2 mono-number">
              {formatCurrency(demoStats.totalSpent / demoPayments.length)}
            </p>
          </div>
          <div className="px-6 py-6">
            <p className="section-header">Savings</p>
            <p className="text-2xl font-medium tracking-tight mt-2 mono-number text-success">
              {formatCurrency(demoStats.monthlySavings)}
            </p>
          </div>
        </div>

        {/* Transaction List Header */}
        <div className="px-8 py-4 border-b border-border">
          <h2 className="section-header">Transaction History</h2>
        </div>

        {/* Transaction List */}
        <div className="stagger-children">
          {demoPayments.map((payment, index) => (
            <div
              key={payment.invoice_id}
              className="px-8 py-5 border-b border-border"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-4">
                  <span className="text-xs text-muted-foreground w-6 font-mono pt-0.5">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <span className="font-medium text-sm">
                        {payment.vendor_name}
                      </span>
                      <Badge
                        variant="outline"
                        className={`text-[10px] uppercase tracking-wider ${getStatusColor(payment.status)}`}
                      >
                        {payment.status}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1 font-mono">
                      {formatDate(payment.date)} &middot; {payment.invoice_id}
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium mono-number">{formatCurrency(payment.amount_usd)}</p>
                </div>
              </div>

              {/* Transaction Details */}
              <div className="mt-3 ml-10 flex flex-wrap gap-x-4 gap-y-1 text-xs text-muted-foreground">
                {payment.x402_tx_hash && (
                  <a
                    href={`https://basescan.org/tx/${payment.x402_tx_hash}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 hover:text-foreground transition-colors font-mono"
                  >
                    x402: {payment.x402_tx_hash.slice(0, 8)}...{payment.x402_tx_hash.slice(-6)}
                    <ExternalLink className="h-3 w-3" />
                  </a>
                )}
                {payment.ach_confirmation && (
                  <span className="font-mono">ACH: {payment.ach_confirmation}</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {demoPayments.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted-foreground text-sm">No transactions yet</p>
          </div>
        )}
      </div>
    </>
  );
}
