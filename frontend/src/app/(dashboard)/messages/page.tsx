"use client";

import { Card, CardContent } from "@/components/ui/card";
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
      <div className="p-6 space-y-6 animate-fade-in max-w-2xl mx-auto">
        {/* Page Title */}
        <div className="hidden md:block">
          <h1 className="text-2xl font-semibold">Messages</h1>
          <p className="text-muted-foreground text-sm mt-1">
            SMS conversation with Haggl
          </p>
        </div>

        {/* Phone Numbers */}
        <Card>
          <CardContent className="p-4 flex justify-between items-center">
            <div>
              <p className="text-xs text-muted-foreground">Your Number</p>
              <p className="text-sm font-medium">{demoProfile.phone}</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Haggl Bot</p>
              <p className="text-sm font-medium">+1-888-HAGGL-AI</p>
            </div>
          </CardContent>
        </Card>

        {/* Messages */}
        <Card>
          <CardContent className="p-4">
            {/* Date Header */}
            <div className="text-center mb-4">
              <Badge variant="secondary" className="text-xs">
                {formatDate(demoMessages[0]?.timestamp || new Date().toISOString())}
              </Badge>
            </div>

            {/* Message List */}
            <div className="space-y-4">
              {demoMessages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    "flex",
                    message.role === "user" ? "justify-end" : "justify-start"
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[80%] rounded-2xl px-4 py-2 animate-fade-in",
                      message.role === "user"
                        ? "bg-primary text-primary-foreground rounded-br-sm"
                        : "bg-secondary text-secondary-foreground rounded-bl-sm"
                    )}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p
                      className={cn(
                        "text-[10px] mt-1",
                        message.role === "user"
                          ? "text-primary-foreground/70"
                          : "text-muted-foreground"
                      )}
                    >
                      {formatTime(message.timestamp)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Help Text */}
        <div className="text-center text-xs text-muted-foreground">
          <p>Text commands: REORDER, ORDER, APPROVE, DENY, STATUS, BUDGET</p>
        </div>
      </div>
    </>
  );
}
