import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { NavBarWrapper } from "@/components/NavBarWrapper";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Haggl - AI Buyer for Small Businesses",
  description: "AI agents that source, negotiate, and pay for your business supplies autonomously",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <NavBarWrapper />
        <main className="min-h-screen bg-white">
          {children}
        </main>
        <Toaster position="bottom-right" />
      </body>
    </html>
  );
}

