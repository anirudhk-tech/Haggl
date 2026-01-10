"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import {
  Home,
  Package,
  Users,
  CreditCard,
  MessageSquare,
  Settings,
  Plus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const navItems = [
  { href: "/", icon: Home, label: "Dashboard" },
  { href: "/vendors", icon: Users, label: "Vendors" },
  { href: "/payments", icon: CreditCard, label: "Payments" },
  { href: "/messages", icon: MessageSquare, label: "Messages" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export function DesktopNav() {
  const pathname = usePathname();

  return (
    <nav className="hidden md:flex flex-col w-56 border-r border-border bg-white h-screen fixed left-0 top-0">
      {/* Logo */}
      <div className="p-6 border-b border-border">
        <Link href="/" className="text-xl font-semibold tracking-tight">
          Haggl
        </Link>
        <Badge variant="secondary" className="ml-2 text-xs">
          Demo
        </Badge>
      </div>

      {/* New Order Button */}
      <div className="p-4">
        <Button asChild className="w-full gap-2">
          <Link href="/order/new">
            <Plus className="h-4 w-4" />
            New Order
          </Link>
        </Button>
      </div>

      {/* Nav Items */}
      <div className="flex-1 px-3 py-2 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== "/" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive
                  ? "bg-secondary text-foreground"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-border">
        <p className="text-xs text-muted-foreground">Demo Business</p>
        <p className="text-xs text-muted-foreground">San Francisco, CA</p>
      </div>
    </nav>
  );
}

export function MobileNav() {
  const pathname = usePathname();

  const mobileItems = [
    { href: "/", icon: Home, label: "Home" },
    { href: "/order/new", icon: Plus, label: "Order" },
    { href: "/vendors", icon: Users, label: "Vendors" },
    { href: "/payments", icon: CreditCard, label: "Payments" },
    { href: "/messages", icon: MessageSquare, label: "Messages" },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-border z-50">
      <div className="flex justify-around items-center h-16">
        {mobileItems.map((item) => {
          const isActive = pathname === item.href ||
            (item.href !== "/" && item.href !== "/order/new" && pathname.startsWith(item.href));

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex flex-col items-center gap-1 px-3 py-2 text-xs transition-colors",
                isActive
                  ? "text-primary"
                  : "text-muted-foreground"
              )}
            >
              <item.icon className={cn("h-5 w-5", item.href === "/order/new" && "text-primary")} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

export function Header({ title }: { title?: string }) {
  return (
    <header className="md:hidden flex items-center justify-between p-4 border-b border-border bg-white sticky top-0 z-40">
      <Link href="/" className="text-lg font-semibold tracking-tight">
        Haggl
      </Link>
      {title && <span className="text-sm text-muted-foreground">{title}</span>}
      <Link href="/settings">
        <Settings className="h-5 w-5 text-muted-foreground" />
      </Link>
    </header>
  );
}
