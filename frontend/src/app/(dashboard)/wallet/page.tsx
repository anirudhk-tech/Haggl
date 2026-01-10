"use client";

import { useState } from "react";
import { Header } from "@/components/layout/nav";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { demoWallet } from "@/lib/demo-data";
import type { Wallet, WalletTransaction } from "@/lib/types";
import {
  Plus,
  ArrowUpRight,
  ArrowDownLeft,
  Clock,
  CreditCard,
  Building2,
  Wallet as WalletIcon,
  RotateCcw,
  Check,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

type DepositMethod = "card" | "bank" | null;

const QUICK_AMOUNTS = [100, 500, 1000, 2500, 5000];

function formatCurrency(amount: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(Math.abs(amount));
}

function formatDate(timestamp: string) {
  return new Date(timestamp).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

function getTransactionIcon(type: WalletTransaction["type"]) {
  switch (type) {
    case "deposit":
      return ArrowDownLeft;
    case "payment":
      return ArrowUpRight;
    case "refund":
      return RotateCcw;
  }
}

function getTransactionColor(type: WalletTransaction["type"]) {
  switch (type) {
    case "deposit":
      return "text-green-600";
    case "payment":
      return "text-foreground";
    case "refund":
      return "text-blue-600";
  }
}

export default function WalletPage() {
  const [wallet, setWallet] = useState<Wallet>(demoWallet);
  const [addFundsOpen, setAddFundsOpen] = useState(false);
  const [depositMethod, setDepositMethod] = useState<DepositMethod>(null);
  const [customAmount, setCustomAmount] = useState("");
  const [selectedAmount, setSelectedAmount] = useState<number | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleAddFunds = async () => {
    const amount = selectedAmount || parseFloat(customAmount);
    if (!amount || amount <= 0 || !depositMethod) {
      toast.error("Please select an amount and payment method");
      return;
    }

    setIsProcessing(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1500));

    const newTransaction: WalletTransaction = {
      id: `txn-${Date.now()}`,
      type: "deposit",
      amount: amount,
      description: depositMethod === "card" ? "Card deposit" : "Bank transfer deposit",
      timestamp: new Date().toISOString(),
      status: "completed",
      reference: depositMethod === "card"
        ? `CARD-DEP-${Math.floor(Math.random() * 100000)}`
        : `ACH-DEP-${Math.floor(Math.random() * 100000)}`,
    };

    setWallet((prev) => ({
      ...prev,
      balance: prev.balance + amount,
      transactions: [newTransaction, ...prev.transactions],
    }));

    toast.success(`${formatCurrency(amount)} added to wallet`, {
      description: depositMethod === "card" ? "Card payment processed" : "Bank transfer initiated",
    });

    setAddFundsOpen(false);
    setDepositMethod(null);
    setCustomAmount("");
    setSelectedAmount(null);
    setIsProcessing(false);
  };

  const handleAmountSelect = (amount: number) => {
    setSelectedAmount(amount);
    setCustomAmount("");
  };

  const handleCustomAmountChange = (value: string) => {
    setCustomAmount(value);
    setSelectedAmount(null);
  };

  return (
    <>
      <Header title="Wallet" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Wallet</h1>
          <p className="page-header-subtitle mt-1">
            Manage your funds and view transactions
          </p>
        </header>

        {/* Balance Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 border-b border-border">
          {/* Available Balance */}
          <div className="px-8 py-6 border-b md:border-b-0 md:border-r border-border">
            <p className="section-header flex items-center gap-2">
              <WalletIcon className="h-4 w-4" />
              Available Balance
            </p>
            <p className="text-4xl font-medium tracking-tight mt-2 font-mono text-green-600">
              {formatCurrency(wallet.balance)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">Ready to spend</p>
          </div>

          {/* Pending */}
          <div className="px-8 py-6 border-b md:border-b-0 md:border-r border-border">
            <p className="section-header flex items-center gap-2">
              <Clock className="h-4 w-4" />
              Pending
            </p>
            <p className="text-4xl font-medium tracking-tight mt-2 font-mono text-yellow-600">
              {formatCurrency(wallet.pending_balance)}
            </p>
            <p className="text-xs text-muted-foreground mt-1">Processing payments</p>
          </div>

          {/* Add Funds Button */}
          <div className="px-8 py-6 flex items-center justify-center">
            <button
              onClick={() => setAddFundsOpen(true)}
              className="fill-hover w-full h-14 flex items-center justify-center gap-2 border border-foreground bg-foreground text-background text-sm font-medium uppercase tracking-wider"
            >
              <Plus className="h-4 w-4 relative z-10" />
              <span className="relative z-10">Add Funds</span>
            </button>
          </div>
        </div>

        {/* Transactions */}
        <div>
          <div className="px-8 py-4 border-b border-border">
            <h2 className="section-header">Transaction History</h2>
          </div>

          <div className="stagger-children">
            {wallet.transactions.map((transaction, index) => {
              const Icon = getTransactionIcon(transaction.type);
              const colorClass = getTransactionColor(transaction.type);

              return (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between px-8 py-5 border-b border-border"
                >
                  <div className="flex items-center gap-4">
                    {/* Index */}
                    <span className="text-xs text-muted-foreground w-6 font-mono">
                      {String(index + 1).padStart(2, "0")}
                    </span>

                    {/* Icon */}
                    <div
                      className={cn(
                        "w-10 h-10 flex items-center justify-center border border-border",
                        transaction.type === "deposit" && "bg-green-50",
                        transaction.type === "refund" && "bg-blue-50"
                      )}
                    >
                      <Icon className={cn("h-4 w-4", colorClass)} />
                    </div>

                    {/* Details */}
                    <div>
                      <p className="text-sm font-medium">{transaction.description}</p>
                      {transaction.vendor_name && (
                        <p className="text-xs text-muted-foreground mt-0.5">
                          {transaction.vendor_name}
                        </p>
                      )}
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-xs text-muted-foreground font-mono">
                          {formatDate(transaction.timestamp)}, {formatTime(transaction.timestamp)}
                        </span>
                        {transaction.reference && (
                          <span className="text-xs text-muted-foreground font-mono">
                            • {transaction.reference}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Amount and Status */}
                  <div className="text-right">
                    <p className={cn("text-lg font-medium font-mono", colorClass)}>
                      {transaction.amount > 0 ? "+" : ""}
                      {formatCurrency(transaction.amount)}
                    </p>
                    <Badge
                      variant="outline"
                      className={cn(
                        "text-[10px] uppercase tracking-wider",
                        transaction.status === "completed" && "border-green-500/50 text-green-600",
                        transaction.status === "pending" && "border-yellow-500/50 text-yellow-600",
                        transaction.status === "failed" && "border-red-500/50 text-red-600"
                      )}
                    >
                      {transaction.status}
                    </Badge>
                  </div>
                </div>
              );
            })}
          </div>

          {wallet.transactions.length === 0 && (
            <div className="text-center py-16">
              <p className="text-muted-foreground text-sm">No transactions yet</p>
            </div>
          )}
        </div>
      </div>

      {/* Add Funds Dialog */}
      <Dialog open={addFundsOpen} onOpenChange={setAddFundsOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="text-lg font-medium">Add Funds</DialogTitle>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Quick Amount Buttons */}
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3">
                Select Amount
              </p>
              <div className="grid grid-cols-3 gap-2">
                {QUICK_AMOUNTS.map((amount) => (
                  <button
                    key={amount}
                    onClick={() => handleAmountSelect(amount)}
                    className={cn(
                      "fill-hover h-12 flex items-center justify-center border text-sm font-mono",
                      selectedAmount === amount
                        ? "border-foreground bg-foreground text-background"
                        : "border-border"
                    )}
                  >
                    <span className="relative z-10">${amount.toLocaleString()}</span>
                  </button>
                ))}
                {/* Custom Amount Input */}
                <div className="col-span-3 mt-2">
                  <div className="flex items-center border border-border">
                    <span className="px-3 text-muted-foreground">$</span>
                    <input
                      type="number"
                      placeholder="Custom amount"
                      value={customAmount}
                      onChange={(e) => handleCustomAmountChange(e.target.value)}
                      className="flex-1 h-12 bg-transparent text-sm font-mono focus:outline-none"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Payment Method */}
            <div>
              <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3">
                Payment Method
              </p>
              <div className="space-y-2">
                <button
                  onClick={() => setDepositMethod("card")}
                  className={cn(
                    "fill-hover w-full h-14 flex items-center gap-4 px-4 border",
                    depositMethod === "card"
                      ? "border-foreground bg-foreground text-background"
                      : "border-border"
                  )}
                >
                  <CreditCard className="h-5 w-5 relative z-10" />
                  <div className="text-left relative z-10">
                    <p className="text-sm font-medium">Credit/Debit Card</p>
                    <p className={cn(
                      "text-xs",
                      depositMethod === "card" ? "text-background/70" : "text-muted-foreground"
                    )}>
                      Instant • 2.9% fee
                    </p>
                  </div>
                  {depositMethod === "card" && (
                    <Check className="h-4 w-4 ml-auto relative z-10" />
                  )}
                </button>
                <button
                  onClick={() => setDepositMethod("bank")}
                  className={cn(
                    "fill-hover w-full h-14 flex items-center gap-4 px-4 border",
                    depositMethod === "bank"
                      ? "border-foreground bg-foreground text-background"
                      : "border-border"
                  )}
                >
                  <Building2 className="h-5 w-5 relative z-10" />
                  <div className="text-left relative z-10">
                    <p className="text-sm font-medium">Bank Transfer (ACH)</p>
                    <p className={cn(
                      "text-xs",
                      depositMethod === "bank" ? "text-background/70" : "text-muted-foreground"
                    )}>
                      1-3 business days • No fee
                    </p>
                  </div>
                  {depositMethod === "bank" && (
                    <Check className="h-4 w-4 ml-auto relative z-10" />
                  )}
                </button>
              </div>
            </div>

            {/* Summary */}
            {(selectedAmount || customAmount) && depositMethod && (
              <div className="border border-border p-4 bg-secondary/30">
                <div className="flex justify-between text-sm">
                  <span className="text-muted-foreground">Amount</span>
                  <span className="font-mono">
                    {formatCurrency(selectedAmount || parseFloat(customAmount) || 0)}
                  </span>
                </div>
                {depositMethod === "card" && (
                  <div className="flex justify-between text-sm mt-2">
                    <span className="text-muted-foreground">Processing fee (2.9%)</span>
                    <span className="font-mono">
                      {formatCurrency((selectedAmount || parseFloat(customAmount) || 0) * 0.029)}
                    </span>
                  </div>
                )}
                <div className="flex justify-between text-sm mt-2 pt-2 border-t border-border font-medium">
                  <span>Total</span>
                  <span className="font-mono">
                    {formatCurrency(
                      (selectedAmount || parseFloat(customAmount) || 0) *
                        (depositMethod === "card" ? 1.029 : 1)
                    )}
                  </span>
                </div>
              </div>
            )}

            {/* Add Funds Button */}
            <button
              onClick={handleAddFunds}
              disabled={(!selectedAmount && !customAmount) || !depositMethod || isProcessing}
              className="fill-hover w-full h-12 flex items-center justify-center gap-2 border border-foreground bg-foreground text-background text-sm font-medium uppercase tracking-wider disabled:opacity-50"
            >
              <span className="relative z-10">
                {isProcessing ? "Processing..." : "Add Funds"}
              </span>
            </button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
