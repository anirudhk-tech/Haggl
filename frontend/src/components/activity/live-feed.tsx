"use client";

import { useEffect, useState, useRef } from "react";
import { Badge } from "@/components/ui/badge";
import type { AgentEvent, AgentStage } from "@/lib/types";
import {
  Search,
  Phone,
  MessageSquare,
  BarChart3,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Clock,
  Zap,
  RefreshCw,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8001";

// Stage icons and colors
const STAGE_CONFIG: Record<AgentStage, { icon: React.ElementType; color: string; label: string }> = {
  idle: { icon: Clock, color: "text-muted-foreground", label: "Idle" },
  message_received: { icon: MessageSquare, color: "text-blue-500", label: "Message" },
  sourcing: { icon: Search, color: "text-amber-500", label: "Sourcing" },
  calling: { icon: Phone, color: "text-orange-500", label: "Calling" },
  negotiating: { icon: Zap, color: "text-purple-500", label: "Negotiating" },
  evaluating: { icon: BarChart3, color: "text-cyan-500", label: "Evaluating" },
  confirmed: { icon: CheckCircle2, color: "text-emerald-500", label: "Confirmed" },
  approval_pending: { icon: AlertCircle, color: "text-yellow-500", label: "Approval" },
  approved: { icon: CheckCircle2, color: "text-green-500", label: "Approved" },
  completed: { icon: CheckCircle2, color: "text-green-600", label: "Done" },
  failed: { icon: AlertCircle, color: "text-red-500", label: "Failed" },
};

function formatTime(timestamp: string) {
  const date = new Date(timestamp);
  return date.toLocaleTimeString("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function EventItem({ event }: { event: AgentEvent }) {
  const config = STAGE_CONFIG[event.stage] || STAGE_CONFIG.idle;
  const Icon = config.icon;

  return (
    <div className="flex items-start gap-3 px-4 py-3 border-b border-border animate-fade-in hover:bg-muted/30 transition-colors">
      <div className={`mt-0.5 ${config.color}`}>
        <Icon className="h-4 w-4" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="outline" className={`text-[10px] ${config.color} border-current`}>
            {config.label}
          </Badge>
          {event.order_id && (
            <span className="text-[10px] text-muted-foreground font-mono">
              {event.order_id}
            </span>
          )}
        </div>
        <p className="text-sm leading-relaxed">{event.message}</p>
        <p className="text-[10px] text-muted-foreground mt-1 font-mono">
          {formatTime(event.timestamp)}
        </p>
      </div>
    </div>
  );
}

export function LiveActivityFeed() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<AgentStage>("idle");
  const feedRef = useRef<HTMLDivElement>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  const fetchRecentEvents = async () => {
    try {
      setError(null);
      const res = await fetch(`${API_URL}/events/recent?limit=50`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.events) {
        setEvents(data.events.reverse());
      }
    } catch (err) {
      console.error("Failed to fetch events:", err);
      setError(`Cannot connect to ${API_URL}`);
    }
  };

  const connectSSE = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }

    const eventSource = new EventSource(`${API_URL}/events/stream`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setConnected(true);
      setError(null);
    };

    eventSource.onmessage = (e) => {
      try {
        const event: AgentEvent = JSON.parse(e.data);
        setEvents((prev) => [event, ...prev].slice(0, 100));
        setCurrentStage(event.stage);
      } catch (err) {
        console.error("Failed to parse event:", err);
      }
    };

    eventSource.onerror = () => {
      setConnected(false);
      setError("Connection lost. Retrying...");
    };

    return eventSource;
  };

  useEffect(() => {
    fetchRecentEvents();
    const eventSource = connectSSE();
    return () => eventSource.close();
  }, []);

  // Auto-scroll to top when new events arrive
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = 0;
    }
  }, [events]);

  const config = STAGE_CONFIG[currentStage];
  const StageIcon = config.icon;

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className={`${connected ? "text-emerald-500" : error ? "text-red-500" : "text-muted-foreground"}`}>
            {connected ? (
              <span className="flex items-center gap-1.5">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-xs uppercase tracking-wider">Live</span>
              </span>
            ) : error ? (
              <span className="flex items-center gap-1.5">
                <AlertCircle className="h-3 w-3" />
                <span className="text-xs uppercase tracking-wider">Error</span>
              </span>
            ) : (
              <span className="flex items-center gap-1.5">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span className="text-xs uppercase tracking-wider">Connecting</span>
              </span>
            )}
          </div>
          <button
            onClick={() => { fetchRecentEvents(); connectSSE(); }}
            className="p-1 hover:bg-muted rounded"
            title="Refresh"
          >
            <RefreshCw className="h-3 w-3" />
          </button>
        </div>
        <Badge variant="outline" className={`${config.color} border-current`}>
          <StageIcon className="h-3 w-3 mr-1" />
          {config.label}
        </Badge>
      </div>
      
      {/* Error Banner */}
      {error && (
        <div className="px-4 py-2 bg-red-500/10 border-b border-red-500/20 text-red-500 text-xs">
          {error}
        </div>
      )}

      {/* Event Feed */}
      <div
        ref={feedRef}
        className="flex-1 overflow-y-auto"
        style={{ maxHeight: "calc(100vh - 200px)" }}
      >
        {events.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-muted-foreground text-sm">
            Waiting for activity...
          </div>
        ) : (
          events.map((event, i) => (
            <EventItem key={`${event.timestamp}-${i}`} event={event} />
          ))
        )}
      </div>
    </div>
  );
}

// Stage progress indicator
export function StageProgress({ currentStage }: { currentStage: AgentStage }) {
  const stages: AgentStage[] = [
    "message_received",
    "sourcing",
    "calling",
    "negotiating",
    "evaluating",
    "approval_pending",
  ];

  const currentIndex = stages.indexOf(currentStage);

  return (
    <div className="flex items-center gap-1 px-4 py-3 border-b border-border overflow-x-auto">
      {stages.map((stage, i) => {
        const config = STAGE_CONFIG[stage];
        const Icon = config.icon;
        const isActive = i <= currentIndex;
        const isCurrent = stage === currentStage;

        return (
          <div key={stage} className="flex items-center">
            <div
              className={`flex items-center gap-1.5 px-2 py-1 rounded-sm text-xs transition-colors
                ${isCurrent ? "bg-foreground text-background" : ""}
                ${isActive && !isCurrent ? config.color : ""}
                ${!isActive ? "text-muted-foreground/50" : ""}
              `}
            >
              <Icon className="h-3 w-3" />
              <span className="hidden sm:inline uppercase tracking-wider">
                {config.label}
              </span>
            </div>
            {i < stages.length - 1 && (
              <div
                className={`w-4 h-px mx-1 ${
                  i < currentIndex ? "bg-foreground" : "bg-border"
                }`}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
