"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/layout/nav";
import { businessTypes, extractedProducts, savedProducts } from "@/lib/demo-data";
import {
  Check,
  Upload,
  ArrowRight,
  ArrowLeft,
  Loader2,
  Building2,
  FileText,
  Package,
  ShoppingCart,
} from "lucide-react";
import { toast } from "sonner";
import { cn } from "@/lib/utils";

type Step = "business" | "source" | "menu" | "products" | "quantities" | "review";
type BusinessType = "restaurant" | "bakery" | "cafe" | "retail" | "other" | null;
type SourceType = "menu" | "saved" | "manual" | null;

interface SelectedProduct {
  id: number;
  name: string;
  category: string;
  unit: string;
  quantity: number;
}

export default function NewOrderPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("business");
  const [businessType, setBusinessType] = useState<BusinessType>(null);
  const [sourceType, setSourceType] = useState<SourceType>(null);
  const [menuFile, setMenuFile] = useState<File | null>(null);
  const [menuText, setMenuText] = useState("");
  const [isExtracting, setIsExtracting] = useState(false);
  const [selectedProductIds, setSelectedProductIds] = useState<Set<number>>(new Set());
  const [selectedProducts, setSelectedProducts] = useState<SelectedProduct[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const needsMenu = businessType === "restaurant" || businessType === "bakery";
  const products = businessType ? extractedProducts[businessType] || [] : [];

  const handleBusinessSelect = (type: BusinessType) => {
    setBusinessType(type);
    setTimeout(() => setStep("source"), 200);
  };

  const handleSourceSelect = (source: SourceType) => {
    setSourceType(source);
    if (source === "menu") {
      setTimeout(() => setStep("menu"), 200);
    } else if (source === "saved") {
      // Use saved products
      setTimeout(() => setStep("products"), 200);
    } else {
      // Manual entry - go to quantities with empty list
      setTimeout(() => setStep("quantities"), 200);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setMenuFile(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setMenuFile(e.dataTransfer.files[0]);
    }
  };

  const handleExtractProducts = async () => {
    if (!menuFile && !menuText.trim()) return;

    setIsExtracting(true);
    // Simulate AI extraction
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsExtracting(false);
    setStep("products");
  };

  const toggleProduct = (productId: number) => {
    setSelectedProductIds((prev) => {
      const next = new Set(prev);
      if (next.has(productId)) {
        next.delete(productId);
      } else {
        next.add(productId);
      }
      return next;
    });
  };

  const handleProductsContinue = () => {
    // Convert selected products to the format we need
    const productSource = sourceType === "saved" ? savedProducts : products;
    const selected = productSource
      .filter((p) => selectedProductIds.has(p.id))
      .map((p) => ({
        id: p.id,
        name: p.name,
        category: p.category,
        unit: p.unit,
        quantity: "typicalQuantity" in p ? p.typicalQuantity : p.estimatedMonthly,
      }));
    setSelectedProducts(selected);
    setStep("quantities");
  };

  const updateQuantity = (productId: number, quantity: number) => {
    setSelectedProducts((prev) =>
      prev.map((p) => (p.id === productId ? { ...p, quantity } : p))
    );
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    await new Promise((resolve) => setTimeout(resolve, 2000));
    toast.success("Order submitted! Finding best vendors...");
    router.push("/approvals");
  };

  const productSource = sourceType === "saved" ? savedProducts : products;
  const estimatedTotal = selectedProducts.reduce(
    (sum, p) => sum + p.quantity * 0.5, // Placeholder price
    0
  );

  const getStepNumber = () => {
    const steps: Step[] = ["business", "source", "menu", "products", "quantities", "review"];
    return steps.indexOf(step) + 1;
  };

  return (
    <>
      <Header title="New Order" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">New Order</h1>
          <p className="page-header-subtitle mt-1">
            {step === "business" && "Select your business type"}
            {step === "source" && "Choose how to add products"}
            {step === "menu" && "Upload your menu"}
            {step === "products" && "Select products to order"}
            {step === "quantities" && "Set quantities"}
            {step === "review" && "Review and submit"}
          </p>
        </header>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-3 px-8 py-4 border-b border-border bg-secondary/20">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center gap-3">
              <div
                className={cn(
                  "w-8 h-8 flex items-center justify-center border text-xs font-mono",
                  getStepNumber() > s
                    ? "bg-foreground text-background border-foreground"
                    : getStepNumber() === s
                    ? "border-foreground"
                    : "border-border text-muted-foreground"
                )}
              >
                {getStepNumber() > s ? <Check className="h-4 w-4" /> : s}
              </div>
              {s < 4 && (
                <div
                  className={cn(
                    "w-12 h-px",
                    getStepNumber() > s ? "bg-foreground" : "bg-border"
                  )}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step: Business Type */}
        {step === "business" && (
          <div className="stagger-children">
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">What type of business are you?</h2>
            </div>
            {businessTypes.map((type) => (
              <button
                key={type.id}
                onClick={() => handleBusinessSelect(type.id as BusinessType)}
                className={cn(
                  "fill-hover w-full flex items-center gap-6 px-8 py-6 border-b border-border text-left",
                  businessType === type.id && "filled"
                )}
              >
                <div className="h-12 w-12 border border-border flex items-center justify-center relative z-10">
                  <Building2 className="h-6 w-6" />
                </div>
                <div className="relative z-10">
                  <h3 className="font-medium text-sm">{type.label}</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    {type.description}
                  </p>
                </div>
                {businessType === type.id && (
                  <Check className="h-5 w-5 ml-auto relative z-10" />
                )}
              </button>
            ))}
          </div>
        )}

        {/* Step: Source Selection */}
        {step === "source" && (
          <div className="stagger-children">
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">How would you like to add products?</h2>
            </div>

            {needsMenu && (
              <button
                onClick={() => handleSourceSelect("menu")}
                className={cn(
                  "fill-hover w-full flex items-center gap-6 px-8 py-6 border-b border-border text-left",
                  sourceType === "menu" && "filled"
                )}
              >
                <div className="h-12 w-12 border border-border flex items-center justify-center relative z-10">
                  <Upload className="h-6 w-6" />
                </div>
                <div className="relative z-10">
                  <h3 className="font-medium text-sm">Upload Menu</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    AI extracts ingredients from your menu
                  </p>
                </div>
              </button>
            )}

            <button
              onClick={() => handleSourceSelect("saved")}
              className={cn(
                "fill-hover w-full flex items-center gap-6 px-8 py-6 border-b border-border text-left",
                sourceType === "saved" && "filled"
              )}
            >
              <div className="h-12 w-12 border border-border flex items-center justify-center relative z-10">
                <Package className="h-6 w-6" />
              </div>
              <div className="relative z-10">
                <h3 className="font-medium text-sm">From Saved Products</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Quick reorder from your product list ({savedProducts.length} items)
                </p>
              </div>
            </button>

            <button
              onClick={() => handleSourceSelect("manual")}
              className={cn(
                "fill-hover w-full flex items-center gap-6 px-8 py-6 border-b border-border text-left",
                sourceType === "manual" && "filled"
              )}
            >
              <div className="h-12 w-12 border border-border flex items-center justify-center relative z-10">
                <FileText className="h-6 w-6" />
              </div>
              <div className="relative z-10">
                <h3 className="font-medium text-sm">Manual Entry</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Add products one by one
                </p>
              </div>
            </button>

            <div className="px-8 py-4">
              <button
                onClick={() => setStep("business")}
                className="fill-hover px-6 h-10 border border-border text-sm font-medium uppercase tracking-wider flex items-center gap-2"
              >
                <ArrowLeft className="h-4 w-4 relative z-10" />
                <span className="relative z-10">Back</span>
              </button>
            </div>
          </div>
        )}

        {/* Step: Menu Upload */}
        {step === "menu" && (
          <div>
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">Upload your menu</h2>
              <p className="text-xs text-muted-foreground mt-1">
                We'll analyze it to identify ingredients you need
              </p>
            </div>

            <div className="px-8 py-8 border-b border-border">
              <div
                onDrop={handleDrop}
                onDragOver={(e) => e.preventDefault()}
                className={cn(
                  "border-2 border-dashed p-12 text-center transition-colors",
                  menuFile ? "border-foreground bg-secondary/30" : "border-border"
                )}
              >
                <Upload className="mx-auto mb-4 text-muted-foreground h-12 w-12" />
                <p className="text-sm font-medium">Drop a file here or browse</p>
                <p className="text-xs text-muted-foreground mt-1">PDF, PNG, JPG, TXT</p>
                <input
                  type="file"
                  onChange={handleFileChange}
                  accept=".pdf,.png,.jpg,.jpeg,.txt"
                  className="hidden"
                  id="menu-upload"
                />
                <label
                  htmlFor="menu-upload"
                  className="fill-hover inline-block mt-4 px-6 py-2 border border-border text-sm font-medium uppercase tracking-wider cursor-pointer"
                >
                  <span className="relative z-10">Browse Files</span>
                </label>
                {menuFile && (
                  <p className="mt-4 text-sm font-mono">{menuFile.name}</p>
                )}
              </div>
            </div>

            <div className="flex items-center gap-4 px-8 py-4 border-b border-border">
              <div className="flex-1 h-px bg-border" />
              <span className="text-xs text-muted-foreground uppercase tracking-wider">or</span>
              <div className="flex-1 h-px bg-border" />
            </div>

            <div className="px-8 py-6 border-b border-border">
              <label className="block text-xs uppercase tracking-wider text-muted-foreground mb-3">
                Paste your menu
              </label>
              <textarea
                value={menuText}
                onChange={(e) => setMenuText(e.target.value)}
                rows={6}
                className="w-full bg-transparent border border-border p-4 text-sm focus:outline-none focus:border-foreground resize-none"
                placeholder="Paste menu items here..."
              />
            </div>

            <div className="flex border-b border-border">
              <button
                onClick={() => setStep("source")}
                className="fill-hover flex items-center justify-center gap-2 px-8 h-12 border-r border-border text-sm font-medium uppercase tracking-wider"
              >
                <ArrowLeft className="h-4 w-4 relative z-10" />
                <span className="relative z-10">Back</span>
              </button>
              <button
                onClick={handleExtractProducts}
                disabled={!menuFile && !menuText.trim()}
                className="fill-hover flex-1 flex items-center justify-center gap-2 h-12 text-sm font-medium uppercase tracking-wider disabled:opacity-50"
              >
                {isExtracting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin relative z-10" />
                    <span className="relative z-10">Analyzing Menu...</span>
                  </>
                ) : (
                  <>
                    <span className="relative z-10">Extract Products</span>
                    <ArrowRight className="h-4 w-4 relative z-10" />
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step: Product Selection */}
        {step === "products" && (
          <div>
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">
                Select products ({selectedProductIds.size} selected)
              </h2>
            </div>

            <div className="stagger-children max-h-[50vh] overflow-y-auto">
              {productSource.map((product) => {
                const isSelected = selectedProductIds.has(product.id);
                return (
                  <button
                    key={product.id}
                    onClick={() => toggleProduct(product.id)}
                    className={cn(
                      "fill-hover w-full flex items-center gap-4 px-8 py-4 border-b border-border text-left",
                      isSelected && "filled"
                    )}
                  >
                    <div
                      className={cn(
                        "h-6 w-6 border flex items-center justify-center relative z-10",
                        isSelected ? "border-background" : "border-border"
                      )}
                    >
                      {isSelected && <Check className="h-4 w-4" />}
                    </div>
                    <div className="flex-1 relative z-10">
                      <h3 className="font-medium text-sm">{product.name}</h3>
                      <p className="text-xs text-muted-foreground">
                        {product.category} •{" "}
                        {"typicalQuantity" in product
                          ? `~${product.typicalQuantity} ${product.unit}/order`
                          : `~${product.estimatedMonthly} ${product.unit}/month`}
                      </p>
                    </div>
                  </button>
                );
              })}
            </div>

            <div className="flex border-b border-border">
              <button
                onClick={() => setStep("source")}
                className="fill-hover flex items-center justify-center gap-2 px-8 h-12 border-r border-border text-sm font-medium uppercase tracking-wider"
              >
                <ArrowLeft className="h-4 w-4 relative z-10" />
                <span className="relative z-10">Back</span>
              </button>
              <button
                onClick={handleProductsContinue}
                disabled={selectedProductIds.size === 0}
                className="fill-hover flex-1 flex items-center justify-center gap-2 h-12 text-sm font-medium uppercase tracking-wider disabled:opacity-50"
              >
                <span className="relative z-10">Continue</span>
                <ArrowRight className="h-4 w-4 relative z-10" />
              </button>
            </div>
          </div>
        )}

        {/* Step: Quantities */}
        {step === "quantities" && (
          <div>
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">Set quantities</h2>
            </div>

            <div className="stagger-children">
              {selectedProducts.map((product, index) => (
                <div
                  key={product.id}
                  className="px-8 py-5 border-b border-border"
                >
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs text-muted-foreground font-mono">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <Badge
                      variant="outline"
                      className="text-[10px] uppercase tracking-wider"
                    >
                      {product.category}
                    </Badge>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <h3 className="font-medium text-sm">{product.name}</h3>
                    </div>
                    <div className="flex items-center gap-2">
                      <input
                        type="number"
                        value={product.quantity}
                        onChange={(e) =>
                          updateQuantity(product.id, parseInt(e.target.value) || 0)
                        }
                        className="w-24 h-10 px-3 bg-transparent border border-border text-sm font-mono text-right focus:outline-none focus:border-foreground"
                      />
                      <span className="text-xs text-muted-foreground w-16">
                        {product.unit}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {selectedProducts.length === 0 && (
              <div className="px-8 py-12 text-center border-b border-border">
                <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-sm text-muted-foreground">No products selected</p>
                <button
                  onClick={() => setStep("products")}
                  className="fill-hover mt-4 px-6 py-2 border border-border text-sm font-medium uppercase tracking-wider"
                >
                  <span className="relative z-10">Select Products</span>
                </button>
              </div>
            )}

            <div className="flex border-b border-border">
              <button
                onClick={() => setStep("products")}
                className="fill-hover flex items-center justify-center gap-2 px-8 h-12 border-r border-border text-sm font-medium uppercase tracking-wider"
              >
                <ArrowLeft className="h-4 w-4 relative z-10" />
                <span className="relative z-10">Back</span>
              </button>
              <button
                onClick={() => setStep("review")}
                disabled={selectedProducts.length === 0}
                className="fill-hover flex-1 flex items-center justify-center gap-2 h-12 text-sm font-medium uppercase tracking-wider disabled:opacity-50"
              >
                <span className="relative z-10">Review Order</span>
                <ArrowRight className="h-4 w-4 relative z-10" />
              </button>
            </div>
          </div>
        )}

        {/* Step: Review */}
        {step === "review" && (
          <div>
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">Order Summary</h2>
            </div>

            <div className="stagger-children">
              {selectedProducts.map((product, index) => (
                <div
                  key={product.id}
                  className="flex items-center justify-between px-8 py-4 border-b border-border"
                >
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-muted-foreground w-6 font-mono">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <div>
                      <p className="font-medium text-sm">{product.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {product.category}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-mono text-sm">
                      {product.quantity} {product.unit}
                    </p>
                    <Badge
                      variant="outline"
                      className="text-[10px] uppercase tracking-wider border-warning text-warning"
                    >
                      Finding vendors...
                    </Badge>
                  </div>
                </div>
              ))}
            </div>

            {/* Summary */}
            <div className="grid grid-cols-2 border-b border-border">
              <div className="px-8 py-6 border-r border-border">
                <p className="text-xs uppercase tracking-wider text-muted-foreground">
                  Items
                </p>
                <p className="text-3xl font-medium tracking-tight mt-2 font-mono">
                  {selectedProducts.length}
                </p>
              </div>
              <div className="px-8 py-6">
                <p className="text-xs uppercase tracking-wider text-muted-foreground">
                  Business Type
                </p>
                <p className="text-lg font-medium tracking-tight mt-2 capitalize">
                  {businessType}
                </p>
              </div>
            </div>

            {/* Actions */}
            <div className="flex border-b border-border">
              <button
                onClick={() => setStep("quantities")}
                className="fill-hover flex items-center justify-center gap-2 px-8 h-14 border-r border-border text-sm font-medium uppercase tracking-wider"
              >
                <ArrowLeft className="h-4 w-4 relative z-10" />
                <span className="relative z-10">Back</span>
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting}
                className="fill-hover flex-1 flex items-center justify-center gap-2 h-14 text-sm font-medium uppercase tracking-wider bg-foreground text-background disabled:opacity-50"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin relative z-10" />
                    <span className="relative z-10">Finding Vendors...</span>
                  </>
                ) : (
                  <>
                    <ShoppingCart className="h-4 w-4 relative z-10" />
                    <span className="relative z-10">Start Negotiation</span>
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
