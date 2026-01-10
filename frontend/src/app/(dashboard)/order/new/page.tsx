"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/layout/nav";
import {
  Plus,
  X,
  FileSpreadsheet,
  PenLine,
  Upload,
  ArrowRight,
  Loader2,
  ArrowLeft,
} from "lucide-react";
import { toast } from "sonner";

interface Ingredient {
  id: string;
  name: string;
  quantity: string;
  unit: string;
  quality: string;
  usePreferred: boolean;
  preferredVendor?: string;
}

const UNITS = ["lbs", "kg", "dozen", "units", "cases", "gallons"];
const QUALITIES = ["Standard", "Premium", "Organic", "Custom"];

export default function NewOrderPage() {
  const [step, setStep] = useState<"method" | "ingredients" | "review">("method");
  const [inputMethod, setInputMethod] = useState<"manual" | "csv" | null>(null);
  const [ingredients, setIngredients] = useState<Ingredient[]>([
    {
      id: "1",
      name: "",
      quantity: "",
      unit: "lbs",
      quality: "Standard",
      usePreferred: false,
    },
  ]);
  const [budget, setBudget] = useState("2000");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addIngredient = () => {
    setIngredients([
      ...ingredients,
      {
        id: Date.now().toString(),
        name: "",
        quantity: "",
        unit: "lbs",
        quality: "Standard",
        usePreferred: false,
      },
    ]);
  };

  const removeIngredient = (id: string) => {
    if (ingredients.length > 1) {
      setIngredients(ingredients.filter((i) => i.id !== id));
    }
  };

  const updateIngredient = (id: string, field: keyof Ingredient, value: string | boolean) => {
    setIngredients(
      ingredients.map((i) =>
        i.id === id ? { ...i, [field]: value } : i
      )
    );
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setIsSubmitting(false);
    toast.success("Order submitted! Searching for vendors...");
  };

  const validIngredients = ingredients.filter(
    (i) => i.name && i.quantity && parseFloat(i.quantity) > 0
  );

  const estimatedTotal = validIngredients.length * 150; // Placeholder

  return (
    <>
      <Header title="New Order" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">New Order</h1>
          <p className="page-header-subtitle mt-1">
            {step === "method" && "Choose how to add ingredients"}
            {step === "ingredients" && "Add your ingredients"}
            {step === "review" && "Review and submit"}
          </p>
        </header>

        {/* Progress Steps */}
        <div className="flex border-b border-border">
          <div className={`flex-1 px-6 py-3 text-xs uppercase tracking-wider text-center border-r border-border ${step === "method" ? "bg-foreground text-background" : ""}`}>
            01 Method
          </div>
          <div className={`flex-1 px-6 py-3 text-xs uppercase tracking-wider text-center border-r border-border ${step === "ingredients" ? "bg-foreground text-background" : ""}`}>
            02 Ingredients
          </div>
          <div className={`flex-1 px-6 py-3 text-xs uppercase tracking-wider text-center ${step === "review" ? "bg-foreground text-background" : ""}`}>
            03 Review
          </div>
        </div>

        {/* Step: Method Selection */}
        {step === "method" && (
          <div className="stagger-children">
            <button
              className={`fill-hover w-full flex items-center gap-6 px-8 py-6 border-b border-border text-left ${inputMethod === "manual" ? "filled" : ""}`}
              onClick={() => setInputMethod("manual")}
            >
              <div className="h-12 w-12 border border-border flex items-center justify-center relative z-10">
                <PenLine className="h-6 w-6" />
              </div>
              <div className="relative z-10">
                <h3 className="font-medium text-sm">Manual Entry</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Add ingredients one by one
                </p>
              </div>
            </button>

            <button
              className={`fill-hover w-full flex items-center gap-6 px-8 py-6 border-b border-border text-left ${inputMethod === "csv" ? "filled" : ""}`}
              onClick={() => setInputMethod("csv")}
            >
              <div className="h-12 w-12 border border-border flex items-center justify-center relative z-10">
                <FileSpreadsheet className="h-6 w-6" />
              </div>
              <div className="relative z-10">
                <h3 className="font-medium text-sm">CSV Import</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Upload a spreadsheet of ingredients
                </p>
              </div>
            </button>

            <div className="w-full flex items-center gap-6 px-8 py-6 border-b border-border opacity-50 cursor-not-allowed">
              <div className="h-12 w-12 border border-border flex items-center justify-center">
                <Upload className="h-6 w-6 text-muted-foreground" />
              </div>
              <div>
                <h3 className="font-medium text-sm">Menu Upload</h3>
                <p className="text-xs text-muted-foreground mt-1">
                  Coming soon - AI extraction from menus
                </p>
              </div>
            </div>

            <div className="px-8 py-6">
              <button
                className="fill-hover w-full h-12 border border-foreground text-sm font-medium uppercase tracking-wider flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={!inputMethod}
                onClick={() => setStep("ingredients")}
              >
                <span className="relative z-10">Continue</span>
                <ArrowRight className="h-4 w-4 relative z-10" />
              </button>
            </div>
          </div>
        )}

        {/* Step: Ingredients (Manual) */}
        {step === "ingredients" && inputMethod === "manual" && (
          <div>
            <div className="px-8 py-4 border-b border-border">
              <h2 className="section-header">Ingredients</h2>
            </div>

            <div className="stagger-children">
              {ingredients.map((ingredient, index) => (
                <div
                  key={ingredient.id}
                  className="px-8 py-6 border-b border-border animate-fade-in"
                >
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-xs uppercase tracking-wider text-muted-foreground font-mono">
                      Item {String(index + 1).padStart(2, "0")}
                    </span>
                    {ingredients.length > 1 && (
                      <button
                        className="fill-hover h-7 w-7 flex items-center justify-center border border-border"
                        onClick={() => removeIngredient(ingredient.id)}
                      >
                        <X className="h-4 w-4 relative z-10" />
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                      <input
                        type="text"
                        placeholder="Ingredient name"
                        value={ingredient.name}
                        onChange={(e) =>
                          updateIngredient(ingredient.id, "name", e.target.value)
                        }
                        className="w-full h-10 px-3 bg-transparent border border-border text-sm focus:outline-none focus:border-foreground"
                      />
                    </div>
                    <input
                      type="number"
                      placeholder="Quantity"
                      value={ingredient.quantity}
                      onChange={(e) =>
                        updateIngredient(ingredient.id, "quantity", e.target.value)
                      }
                      className="w-full h-10 px-3 bg-transparent border border-border text-sm font-mono focus:outline-none focus:border-foreground"
                    />
                    <select
                      value={ingredient.unit}
                      onChange={(e) =>
                        updateIngredient(ingredient.id, "unit", e.target.value)
                      }
                      className="w-full h-10 px-3 bg-transparent border border-border text-sm focus:outline-none focus:border-foreground"
                    >
                      {UNITS.map((unit) => (
                        <option key={unit} value={unit}>
                          {unit}
                        </option>
                      ))}
                    </select>
                    <select
                      value={ingredient.quality}
                      onChange={(e) =>
                        updateIngredient(ingredient.id, "quality", e.target.value)
                      }
                      className="col-span-2 w-full h-10 px-3 bg-transparent border border-border text-sm focus:outline-none focus:border-foreground"
                    >
                      {QUALITIES.map((q) => (
                        <option key={q} value={q}>
                          {q}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ))}
            </div>

            <button
              className="fill-hover w-full flex items-center justify-center gap-2 h-12 border-b border-border text-sm font-medium uppercase tracking-wider"
              onClick={addIngredient}
            >
              <Plus className="h-4 w-4 relative z-10" />
              <span className="relative z-10">Add Ingredient</span>
            </button>

            {/* Budget */}
            <div className="px-8 py-6 border-b border-border">
              <h2 className="section-header mb-4">Budget</h2>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">$</span>
                <input
                  type="number"
                  value={budget}
                  onChange={(e) => setBudget(e.target.value)}
                  className="w-32 h-10 px-3 bg-transparent border border-border text-sm font-mono focus:outline-none focus:border-foreground"
                />
              </div>
            </div>

            {/* Navigation */}
            <div className="flex border-b border-border">
              <button
                className="fill-hover flex items-center justify-center gap-2 px-8 h-12 border-r border-border text-sm font-medium uppercase tracking-wider"
                onClick={() => setStep("method")}
              >
                <ArrowLeft className="h-4 w-4 relative z-10" />
                <span className="relative z-10">Back</span>
              </button>
              <button
                className="fill-hover flex-1 flex items-center justify-center gap-2 h-12 text-sm font-medium uppercase tracking-wider disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={validIngredients.length === 0}
                onClick={() => setStep("review")}
              >
                <span className="relative z-10">Review Order</span>
                <ArrowRight className="h-4 w-4 relative z-10" />
              </button>
            </div>
          </div>
        )}

        {/* Step: Ingredients (CSV) */}
        {step === "ingredients" && inputMethod === "csv" && (
          <div>
            <div className="px-8 py-12 border-b border-border">
              <div className="border-2 border-dashed border-border p-12 text-center">
                <FileSpreadsheet className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="font-medium text-sm">Drop CSV file here</p>
                <p className="text-xs text-muted-foreground mt-1">
                  or click to browse
                </p>
                <button className="fill-hover mt-6 px-6 py-2 border border-border text-sm font-medium uppercase tracking-wider">
                  <span className="relative z-10">Browse Files</span>
                </button>
              </div>
              <div className="mt-6 text-xs text-muted-foreground">
                <p>Required columns: ingredient, quantity</p>
                <p>Optional: unit, quality, priority</p>
              </div>
            </div>

            <div className="px-8 py-6">
              <button
                className="fill-hover flex items-center justify-center gap-2 px-6 h-10 border border-border text-sm font-medium uppercase tracking-wider"
                onClick={() => setStep("method")}
              >
                <ArrowLeft className="h-4 w-4 relative z-10" />
                <span className="relative z-10">Back</span>
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
              {validIngredients.map((ingredient, index) => (
                <div
                  key={ingredient.id}
                  className="flex items-center justify-between px-8 py-4 border-b border-border"
                >
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-muted-foreground w-6 font-mono">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <div>
                      <p className="font-medium text-sm">{ingredient.name}</p>
                      <p className="text-xs text-muted-foreground font-mono">
                        {ingredient.quantity} {ingredient.unit} &middot;{" "}
                        {ingredient.quality}
                      </p>
                    </div>
                  </div>
                  <Badge variant="outline" className="text-[10px] uppercase tracking-wider border-warning text-warning">
                    Finding vendors...
                  </Badge>
                </div>
              ))}
            </div>

            {/* Totals */}
            <div className="grid grid-cols-2 border-b border-border">
              <div className="px-8 py-6 border-r border-border">
                <p className="text-xs uppercase tracking-wider text-muted-foreground">
                  Estimated Total
                </p>
                <p className="text-3xl font-medium tracking-tight mt-2 font-mono">
                  ${estimatedTotal.toFixed(2)}
                </p>
              </div>
              <div className="px-8 py-6">
                <p className="text-xs uppercase tracking-wider text-muted-foreground">
                  Budget
                </p>
                <p className="text-3xl font-medium tracking-tight mt-2 font-mono">
                  ${budget}
                </p>
              </div>
            </div>

            {/* Navigation */}
            <div className="flex border-b border-border">
              <button
                className="fill-hover flex items-center justify-center gap-2 px-8 h-14 border-r border-border text-sm font-medium uppercase tracking-wider"
                onClick={() => setStep("ingredients")}
              >
                <ArrowLeft className="h-4 w-4 relative z-10" />
                <span className="relative z-10">Back</span>
              </button>
              <button
                className="fill-hover flex-1 flex items-center justify-center gap-2 h-14 text-sm font-medium uppercase tracking-wider disabled:opacity-50"
                onClick={handleSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin relative z-10" />
                    <span className="relative z-10">Finding Vendors...</span>
                  </>
                ) : (
                  <span className="relative z-10">Find Vendors</span>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
