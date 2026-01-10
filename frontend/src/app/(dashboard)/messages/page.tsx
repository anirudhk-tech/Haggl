"use client";

import { useState, useMemo } from "react";
import { Header } from "@/components/layout/nav";
import { demoVendorMessages } from "@/lib/demo-data";
import { cn } from "@/lib/utils";
import {
  Search,
  Phone,
  MessageSquare,
  ChevronDown,
  ChevronUp,
  ArrowUpRight,
  ArrowDownLeft,
  SortAsc,
  Clock,
  Users,
} from "lucide-react";

type SortOption = "recent" | "name" | "messages";

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

function formatDate(timestamp: string) {
  const date = new Date(timestamp);
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}

function formatRelativeTime(timestamp: string) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return formatDate(timestamp);
}

export default function MessagesPage() {
  const [search, setSearch] = useState("");
  const [sortBy, setSortBy] = useState<SortOption>("recent");
  const [expandedTranscripts, setExpandedTranscripts] = useState<Set<string>>(new Set());
  const [collapsedVendors, setCollapsedVendors] = useState<Set<string>>(new Set());

  // Group and sort messages by vendor
  const { vendorList, messagesByVendor } = useMemo(() => {
    const grouped: Record<string, typeof demoVendorMessages> = {};

    let filtered = demoVendorMessages;
    if (search) {
      const lower = search.toLowerCase();
      filtered = demoVendorMessages.filter(
        (m) =>
          m.vendor_name.toLowerCase().includes(lower) ||
          m.content.toLowerCase().includes(lower)
      );
    }

    filtered.forEach((message) => {
      if (!grouped[message.vendor_id]) {
        grouped[message.vendor_id] = [];
      }
      grouped[message.vendor_id].push(message);
    });

    // Sort messages within each vendor by timestamp (newest first)
    Object.keys(grouped).forEach((vendorId) => {
      grouped[vendorId].sort(
        (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );
    });

    // Create vendor list with metadata for sorting
    const vendors = Object.keys(grouped).map((vendorId) => {
      const messages = grouped[vendorId];
      const latestMessage = messages[0];
      return {
        vendorId,
        vendorName: latestMessage?.vendor_name || "Unknown",
        messageCount: messages.length,
        latestTimestamp: latestMessage?.timestamp || "",
        callCount: messages.filter((m) => m.type === "call").length,
        smsCount: messages.filter((m) => m.type === "sms").length,
      };
    });

    // Sort vendors based on selected option
    vendors.sort((a, b) => {
      switch (sortBy) {
        case "recent":
          return new Date(b.latestTimestamp).getTime() - new Date(a.latestTimestamp).getTime();
        case "name":
          return a.vendorName.localeCompare(b.vendorName);
        case "messages":
          return b.messageCount - a.messageCount;
        default:
          return 0;
      }
    });

    return { vendorList: vendors, messagesByVendor: grouped };
  }, [search, sortBy]);

  const toggleTranscript = (messageId: string) => {
    setExpandedTranscripts((prev) => {
      const next = new Set(prev);
      if (next.has(messageId)) {
        next.delete(messageId);
      } else {
        next.add(messageId);
      }
      return next;
    });
  };

  const toggleVendor = (vendorId: string) => {
    setCollapsedVendors((prev) => {
      const next = new Set(prev);
      if (next.has(vendorId)) {
        next.delete(vendorId);
      } else {
        next.add(vendorId);
      }
      return next;
    });
  };

  const totalMessages = vendorList.reduce((sum, v) => sum + v.messageCount, 0);

  return (
    <>
      <Header title="Messages" />
      <div className="animate-fade-in">
        {/* Page Header */}
        <header className="hidden md:block px-8 py-8 border-b border-border">
          <h1 className="page-header">Messages</h1>
          <p className="page-header-subtitle mt-1">
            {vendorList.length} vendor{vendorList.length !== 1 ? "s" : ""} • {totalMessages} message{totalMessages !== 1 ? "s" : ""}
          </p>
        </header>

        {/* Search and Sort Bar */}
        <div className="flex items-center gap-3 px-6 py-3 border-b border-border">
          <Search className="h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search vendors or messages..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent text-sm placeholder:text-muted-foreground focus:outline-none"
          />
        </div>

        {/* Sort Options */}
        <div className="flex items-center gap-2 px-6 py-3 border-b border-border bg-secondary/20">
          <span className="text-xs text-muted-foreground uppercase tracking-wider mr-2">Sort by:</span>
          <button
            onClick={() => setSortBy("recent")}
            className={cn(
              "fill-hover px-3 py-1.5 text-xs border flex items-center gap-1.5",
              sortBy === "recent" ? "border-foreground bg-foreground text-background" : "border-border"
            )}
          >
            <Clock className="h-3 w-3 relative z-10" />
            <span className="relative z-10">Recent</span>
          </button>
          <button
            onClick={() => setSortBy("name")}
            className={cn(
              "fill-hover px-3 py-1.5 text-xs border flex items-center gap-1.5",
              sortBy === "name" ? "border-foreground bg-foreground text-background" : "border-border"
            )}
          >
            <SortAsc className="h-3 w-3 relative z-10" />
            <span className="relative z-10">Name</span>
          </button>
          <button
            onClick={() => setSortBy("messages")}
            className={cn(
              "fill-hover px-3 py-1.5 text-xs border flex items-center gap-1.5",
              sortBy === "messages" ? "border-foreground bg-foreground text-background" : "border-border"
            )}
          >
            <MessageSquare className="h-3 w-3 relative z-10" />
            <span className="relative z-10">Most Messages</span>
          </button>
        </div>

        {/* Vendor Conversations */}
        <div className="stagger-children">
          {vendorList.map((vendor, index) => {
            const messages = messagesByVendor[vendor.vendorId];
            const isCollapsed = collapsedVendors.has(vendor.vendorId);

            return (
              <div key={vendor.vendorId} className="border-b border-border">
                {/* Vendor Header - Clickable */}
                <button
                  onClick={() => toggleVendor(vendor.vendorId)}
                  className="w-full px-6 py-4 bg-secondary/30 hover:bg-secondary/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      {/* Index */}
                      <span className="text-xs text-muted-foreground font-mono w-6">
                        {String(index + 1).padStart(2, "0")}
                      </span>
                      {/* Vendor Name */}
                      <h2 className="text-sm font-medium uppercase tracking-wider text-left">
                        {vendor.vendorName}
                      </h2>
                      {/* Last activity */}
                      <span className="text-xs text-muted-foreground font-mono">
                        {formatRelativeTime(vendor.latestTimestamp)}
                      </span>
                    </div>
                    <div className="flex items-center gap-4">
                      {/* Stats */}
                      <div className="flex items-center gap-3 text-xs text-muted-foreground">
                        {vendor.callCount > 0 && (
                          <span className="flex items-center gap-1 font-mono">
                            <Phone className="h-3 w-3" />
                            {vendor.callCount}
                          </span>
                        )}
                        {vendor.smsCount > 0 && (
                          <span className="flex items-center gap-1 font-mono">
                            <MessageSquare className="h-3 w-3" />
                            {vendor.smsCount}
                          </span>
                        )}
                      </div>
                      {/* Expand/Collapse */}
                      {isCollapsed ? (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronUp className="h-4 w-4 text-muted-foreground" />
                      )}
                    </div>
                  </div>
                </button>

                {/* Messages List - Collapsible */}
                {!isCollapsed && (
                  <div>
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className="px-6 py-4 border-t border-border"
                      >
                        <div className="flex items-start gap-4">
                          {/* Icon */}
                          <div
                            className={cn(
                              "flex-shrink-0 w-8 h-8 flex items-center justify-center border border-border",
                              message.type === "call" ? "bg-secondary/50" : ""
                            )}
                          >
                            {message.type === "call" ? (
                              <Phone className="h-4 w-4" />
                            ) : (
                              <MessageSquare className="h-4 w-4" />
                            )}
                          </div>

                          {/* Content */}
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2">
                              {/* Direction indicator */}
                              {message.direction === "outbound" ? (
                                <ArrowUpRight className="h-3 w-3 text-muted-foreground" />
                              ) : (
                                <ArrowDownLeft className="h-3 w-3 text-muted-foreground" />
                              )}
                              <span className="text-xs text-muted-foreground font-mono">
                                {formatDate(message.timestamp)}, {formatTime(message.timestamp)}
                              </span>
                              {message.type === "call" && message.duration && (
                                <span className="text-xs text-muted-foreground font-mono">
                                  ({message.duration})
                                </span>
                              )}
                            </div>

                            <p className="text-sm mt-1">{message.content}</p>

                            {/* Transcript Toggle */}
                            {message.type === "call" && message.transcript && (
                              <button
                                onClick={() => toggleTranscript(message.id)}
                                className="fill-hover mt-3 px-3 py-1.5 text-xs border border-border flex items-center gap-2"
                              >
                                <span className="relative z-10 uppercase tracking-wider">
                                  {expandedTranscripts.has(message.id)
                                    ? "Hide Transcript"
                                    : "View Transcript"}
                                </span>
                                {expandedTranscripts.has(message.id) ? (
                                  <ChevronUp className="h-3 w-3 relative z-10" />
                                ) : (
                                  <ChevronDown className="h-3 w-3 relative z-10" />
                                )}
                              </button>
                            )}

                            {/* Expanded Transcript */}
                            {message.transcript &&
                              expandedTranscripts.has(message.id) && (
                                <div className="mt-3 p-4 bg-secondary/30 border border-border">
                                  <p className="text-xs uppercase tracking-wider text-muted-foreground mb-3">
                                    Call Transcript
                                  </p>
                                  <pre className="text-xs font-mono whitespace-pre-wrap leading-relaxed">
                                    {message.transcript}
                                  </pre>
                                </div>
                              )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Empty State */}
        {vendorList.length === 0 && (
          <div className="text-center py-16">
            <p className="text-muted-foreground text-sm">No messages found</p>
            {search && (
              <button
                className="fill-hover mt-4 px-4 py-2 text-sm border border-border"
                onClick={() => setSearch("")}
              >
                <span className="relative z-10">Clear search</span>
              </button>
            )}
          </div>
        )}
      </div>
    </>
  );
}
