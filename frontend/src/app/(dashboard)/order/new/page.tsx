"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Header } from "@/components/layout/nav";
import { demoVendors } from "@/lib/demo-data";
import {
  Plus,
  X,
  FileSpreadsheet,
  PenLine,
  Upload,
  ArrowRight,
  Loader2,
} from "lucide-react";
import Link from "next/link";
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
      <div className="p-6 space-y-6 animate-fade-in max-w-2xl mx-auto">
        {/* Page Title */}
        <div>
          <h1 className="text-2xl font-semibold">New Order</h1>
          <p className="text-muted-foreground text-sm mt-1">
            {step === "method" && "Choose how to add ingredients"}
            {step === "ingredients" && "Add your ingredients"}
            {step === "review" && "Review and submit"}
          </p>
        </div>

        {/* Step: Method Selection */}
        {step === "method" && (
          <div className="grid gap-4 stagger-children">
            <Card
              className={`cursor-pointer transition-all hover:border-primary ${
                inputMethod === "manual" ? "border-primary ring-1 ring-primary" : ""
              }`}
              onClick={() => setInputMethod("manual")}
            >
              <CardContent className="p-6 flex items-center gap-4">
                <div className="h-12 w-12 rounded-lg bg-secondary flex items-center justify-center">
                  <PenLine className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-medium">Manual Entry</h3>
                  <p className="text-sm text-muted-foreground">
                    Add ingredients one by one
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card
              className={`cursor-pointer transition-all hover:border-primary ${
                inputMethod === "csv" ? "border-primary ring-1 ring-primary" : ""
              }`}
              onClick={() => setInputMethod("csv")}
            >
              <CardContent className="p-6 flex items-center gap-4">
                <div className="h-12 w-12 rounded-lg bg-secondary flex items-center justify-center">
                  <FileSpreadsheet className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-medium">CSV Import</h3>
                  <p className="text-sm text-muted-foreground">
                    Upload a spreadsheet of ingredients
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card className="cursor-not-allowed opacity-50">
              <CardContent className="p-6 flex items-center gap-4">
                <div className="h-12 w-12 rounded-lg bg-secondary flex items-center justify-center">
                  <Upload className="h-6 w-6 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="font-medium">Menu Upload</h3>
                  <p className="text-sm text-muted-foreground">
                    Coming soon - AI extraction from menus
                  </p>
                </div>
              </CardContent>
            </Card>

            <Button
              className="mt-4"
              disabled={!inputMethod}
              onClick={() => setStep("ingredients")}
            >
              Continue
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        )}

        {/* Step: Ingredients */}
        {step === "ingredients" && inputMethod === "manual" && (
          <div className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Ingredients</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {ingredients.map((ingredient, index) => (
                  <div
                    key={ingredient.id}
                    className="p-4 border rounded-lg space-y-3 animate-fade-in"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-muted-foreground">
                        Item {index + 1}
                      </span>
                      {ingredients.length > 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0"
                          onClick={() => removeIngredient(ingredient.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-3">
                      <div className="col-span-2">
                        <Input
                          placeholder="Ingredient name"
                          value={ingredient.name}
                          onChange={(e) =>
                            updateIngredient(ingredient.id, "name", e.target.value)
                          }
                        />
                      </div>
                      <Input
                        type="number"
                        placeholder="Quantity"
                        value={ingredient.quantity}
                        onChange={(e) =>
                          updateIngredient(ingredient.id, "quantity", e.target.value)
                        }
                      />
                      <Select
                        value={ingredient.unit}
                        onValueChange={(v) =>
                          updateIngredient(ingredient.id, "unit", v)
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {UNITS.map((unit) => (
                            <SelectItem key={unit} value={unit}>
                              {unit}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Select
                        value={ingredient.quality}
                        onValueChange={(v) =>
                          updateIngredient(ingredient.id, "quality", v)
                        }
                      >
                        <SelectTrigger className="col-span-2">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {QUALITIES.map((q) => (
                            <SelectItem key={q} value={q}>
                              {q}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                ))}

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={addIngredient}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Ingredient
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Budget</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">$</span>
                  <Input
                    type="number"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                    className="max-w-32"
                  />
                </div>
              </CardContent>
            </Card>

            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setStep("method")}>
                Back
              </Button>
              <Button
                className="flex-1"
                disabled={validIngredients.length === 0}
                onClick={() => setStep("review")}
              >
                Review Order
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </div>
        )}

        {/* Step: Ingredients (CSV) */}
        {step === "ingredients" && inputMethod === "csv" && (
          <div className="space-y-4">
            <Card>
              <CardContent className="p-8">
                <div className="border-2 border-dashed border-border rounded-lg p-8 text-center">
                  <FileSpreadsheet className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="font-medium">Drop CSV file here</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    or click to browse
                  </p>
                  <Button variant="outline" className="mt-4">
                    Browse Files
                  </Button>
                </div>
                <div className="mt-4 text-xs text-muted-foreground">
                  <p>Required columns: ingredient, quantity</p>
                  <p>Optional: unit, quality, priority</p>
                </div>
              </CardContent>
            </Card>

            <Button variant="outline" onClick={() => setStep("method")}>
              Back
            </Button>
          </div>
        )}

        {/* Step: Review */}
        {step === "review" && (
          <div className="space-y-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {validIngredients.map((ingredient) => (
                  <div
                    key={ingredient.id}
                    className="flex items-center justify-between py-2 border-b last:border-0"
                  >
                    <div>
                      <p className="font-medium text-sm">{ingredient.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {ingredient.quantity} {ingredient.unit} &middot;{" "}
                        {ingredient.quality}
                      </p>
                    </div>
                    <Badge variant="secondary">Finding vendors...</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Estimated Total
                    </p>
                    <p className="text-2xl font-semibold">
                      ${estimatedTotal.toFixed(2)}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">Budget</p>
                    <p className="text-lg font-medium">${budget}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="flex gap-3">
              <Button variant="outline" onClick={() => setStep("ingredients")}>
                Back
              </Button>
              <Button
                className="flex-1"
                onClick={handleSubmit}
                disabled={isSubmitting}
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Finding Vendors...
                  </>
                ) : (
                  "Find Vendors"
                )}
              </Button>
            </div>
          </div>
        )}
      </div>
    </>
  );
}
