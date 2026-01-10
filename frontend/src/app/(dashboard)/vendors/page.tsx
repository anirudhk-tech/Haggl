"use client";

import { useState, useMemo } from "react";
import { Header } from "@/components/layout/nav";
import { VendorCard } from "@/components/vendors/vendor-card";
import { CorrectionDialog } from "@/components/vendors/correction-dialog";
import { demoVendors } from "@/lib/demo-data";
import type { Vendor } from "@/lib/types";
import { Search } from "lucide-react";

export default function VendorsPage() {
  const [search, setSearch] = useState("");
  const [selectedVendor, setSelectedVendor] = useState<Vendor | null>(null);
  const [correctionDialogOpen, setCorrectionDialogOpen] = useState(false);

  const vendors = useMemo(() => {
    let filtered = demoVendors;
    if (search) {
      const lower = search.toLowerCase();
      filtered = demoVendors.filter(
        (v) =>
          v.vendor_name.toLowerCase().includes(lower) ||
          v.products.some((p) => p.toLowerCase().includes(lower))
      );
    }
    // Sort by final_score and assign ranks
    return filtered
      .sort((a, b) => b.final_score - a.final_score)
      .map((v, i) => ({ ...v, rank: i + 1 }));
  }, [search]);

  const handleChartClick = (vendor: Vendor) => {
    setSelectedVendor(vendor);
    setCorrectionDialogOpen(true);
  };

  const handleCorrection = (vendorId: string, parameter: string, direction: "up" | "down") => {
    // In production, this would call the backend API
    console.log("Correction:", { vendorId, parameter, direction });
    // The backend would update the model and return new scores
  };

  return (
    <>
      <Header title="Vendors" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Vendors</h1>
          <p className="page-header-subtitle mt-1">
            {vendors.length} vendors ranked by model predictions
          </p>
        </header>

        {/* Search Bar */}
        <div className="flex items-center gap-3 px-6 py-3 border-b border-border">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search vendors or products..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none"
          />
        </div>

        {/* Instructions */}
        <div className="px-6 py-3 border-b border-border bg-secondary/30">
          <p className="text-xs text-muted-foreground">
            Click on any vendor's score chart to view details and submit corrections to improve predictions.
          </p>
        </div>

        {/* Vendor List */}
        <div className="stagger-children">
          {vendors.map((vendor, index) => (
            <VendorCard
              key={vendor.vendor_id}
              vendor={vendor}
              index={index}
              onChartClick={handleChartClick}
            />
          ))}
        </div>

        {vendors.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted-foreground text-sm">No vendors found</p>
            <button
              className="fill-hover mt-4 px-4 py-2 text-sm border border-border"
              onClick={() => setSearch("")}
            >
              <span className="relative z-10">Clear search</span>
            </button>
          </div>
        )}
      </div>

      {/* Correction Dialog */}
      {selectedVendor && (
        <CorrectionDialog
          vendor={selectedVendor}
          open={correctionDialogOpen}
          onOpenChange={setCorrectionDialogOpen}
          onCorrection={handleCorrection}
        />
      )}
    </>
  );
}
