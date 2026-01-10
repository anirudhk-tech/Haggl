"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import {
  Home,
  Package,
  Users,
  CreditCard,
  MessageSquare,
  Settings,
  Plus,
  ArrowUpRight,
  Activity,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";

const navItems = [
  { href: "/", icon: Home, label: "Dashboard" },
  { href: "/orders", icon: Activity, label: "Orders" },
  { href: "/vendors", icon: Users, label: "Vendors" },
  { href: "/payments", icon: CreditCard, label: "Payments" },
  { href: "/messages", icon: MessageSquare, label: "Messages" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export function DesktopNav() {
  const pathname = usePathname();

  return (
    <nav className="hidden md:flex flex-col w-56 border-r border-border bg-background h-screen fixed left-0 top-0">
      {/* Logo */}
      <div className="px-6 py-5 border-b border-border">
        <Link href="/" className="text-xl font-medium tracking-tight">
          Haggl
        </Link>
        <Badge variant="outline" className="ml-2 text-[10px] uppercase tracking-wider border-border">
          Demo
        </Badge>
      </div>

      {/* New Order Button */}
      <div className="p-4 border-b border-border">
        <Link
          href="/order/new"
          className="fill-hover flex items-center justify-center gap-2 h-10 px-4 border border-foreground/20 text-sm font-medium transition-colors"
        >
          <Plus className="h-4 w-4" />
          <span>New Order</span>
        </Link>
      </div>

      {/* Nav Items */}
      <div className="flex-1 py-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "relative flex items-center gap-3 px-6 py-3 text-sm font-medium border-b border-border transition-colors",
                isActive
                  ? "filled"
                  : "fill-hover"
              )}
            >
              <item.icon className="h-4 w-4 relative z-10" />
              <span className="relative z-10">{item.label}</span>
              {isActive && (
                <ArrowUpRight className="h-3 w-3 ml-auto relative z-10" />
              )}
            </Link>
          );
        })}
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-border">
        <p className="text-xs text-muted-foreground uppercase tracking-wider">Demo Business</p>
        <p className="text-xs text-muted-foreground mt-1">San Francisco, CA</p>
      </div>
    </nav>
  );
}

export function MobileNav() {
  const pathname = usePathname();

  const mobileItems = [
    { href: "/", icon: Home, label: "Home" },
    { href: "/orders", icon: Activity, label: "Orders" },
    { href: "/order/new", icon: Plus, label: "New" },
    { href: "/vendors", icon: Users, label: "Vendors" },
    { href: "/messages", icon: MessageSquare, label: "Chat" },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-background border-t border-border z-50">
      <div className="flex justify-around items-center h-16">
        {mobileItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== "/" && item.href !== "/order/new" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "fill-hover-vertical flex flex-col items-center justify-center gap-1 px-4 py-2 text-[10px] uppercase tracking-wider",
                isActive && "selected"
              )}
            >
              <item.icon className="h-5 w-5 relative z-10" />
              <span className="relative z-10">{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

export function Header({ title }: { title?: string }) {
  return (
    <header className="md:hidden flex items-center justify-between px-5 py-4 border-b border-border bg-background sticky top-0 z-40">
      <Link href="/" className="text-lg font-medium tracking-tight">
        Haggl
      </Link>
      {title && (
        <span className="text-xs uppercase tracking-wider text-muted-foreground">
          {title}
        </span>
      )}
      <Link href="/settings" className="fill-hover p-2 -mr-2">
        <Settings className="h-5 w-5 relative z-10" />
      </Link>
    </header>
  );
}
