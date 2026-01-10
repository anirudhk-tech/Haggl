"use client";

import { Badge } from "@/components/ui/badge";
import { Header } from "@/components/layout/nav";
import { demoMessages, demoProfile } from "@/lib/demo-data";
import { cn } from "@/lib/utils";

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatDate(timestamp: string) {
  const date = new Date(timestamp);
  const today = new Date();
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);

  if (date.toDateString() === today.toDateString()) {
    return "Today";
  } else if (date.toDateString() === yesterday.toDateString()) {
    return "Yesterday";
  } else {
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  }
}

export default function MessagesPage() {
  return (
    <>
      <Header title="Messages" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Messages</h1>
          <p className="page-header-subtitle mt-1">
            SMS conversation with Haggl
          </p>
        </header>

        {/* Phone Numbers */}
        <div className="flex border-b border-border">
          <div className="flex-1 px-8 py-4 border-r border-border">
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Your Number</p>
            <p className="text-sm font-medium font-mono mt-1">{demoProfile.phone}</p>
          </div>
          <div className="flex-1 px-8 py-4">
            <p className="text-xs uppercase tracking-wider text-muted-foreground">Haggl Bot</p>
            <p className="text-sm font-medium font-mono mt-1">+1-888-HAGGL-AI</p>
          </div>
        </div>

        {/* Messages Container */}
        <div className="px-8 py-6 border-b border-border">
          {/* Date Header */}
          <div className="text-center mb-6">
            <Badge variant="outline" className="text-[10px] uppercase tracking-wider border-border">
              {formatDate(demoMessages[0]?.timestamp || new Date().toISOString())}
            </Badge>
          </div>

          {/* Message List */}
          <div className="space-y-4 max-w-2xl mx-auto">
            {demoMessages.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex animate-fade-in",
                  message.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                <div
                  className={cn(
                    "max-w-[80%] px-4 py-3 border",
                    message.role === "user"
                      ? "bg-foreground text-background border-foreground"
                      : "bg-transparent text-foreground border-border"
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  <p
                    className={cn(
                      "text-[10px] mt-2 font-mono",
                      message.role === "user"
                        ? "text-background/70"
                        : "text-muted-foreground"
                    )}
                  >
                    {formatTime(message.timestamp)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Help Text */}
        <div className="px-8 py-4 text-center">
          <p className="text-xs uppercase tracking-wider text-muted-foreground">
            Commands: REORDER, ORDER, APPROVE, DENY, STATUS, BUDGET
          </p>
        </div>
      </div>
    </>
  );
}
