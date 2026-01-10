'use client';

import { useState, useEffect, useCallback } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// Agent stages from backend
export type AgentStage =
  | 'idle'
  | 'message_received'
  | 'sourcing'
  | 'calling'
  | 'negotiating'
  | 'evaluating'
  | 'confirmed'
  | 'approval_pending'
  | 'approved'
  | 'completed'
  | 'failed';

export type EventType =
  | 'stage_change'
  | 'log'
  | 'vendor_update'
  | 'call_update'
  | 'evaluation_update'
  | 'order_update'
  | 'approval_required'
  | 'system';

export interface AgentEvent {
  event_type: EventType;
  stage: AgentStage;
  order_id?: string;
  message: string;
  data: Record<string, unknown>;
  timestamp: string;
}

export interface PendingApproval {
  order_id: string;
  vendor_name: string;
  price: number;
  product: string;
  quantity: number;
  unit: string;
}

// Map backend stages to UI phases
export function stageToPhase(stage: AgentStage): string {
  switch (stage) {
    case 'sourcing':
      return 'sourcing';
    case 'calling':
    case 'negotiating':
      return 'negotiating';
    case 'evaluating':
      return 'evaluating';
    case 'approval_pending':
    case 'confirmed':
      return 'approval';
    case 'approved':
      return 'payment';
    case 'completed':
      return 'complete';
    default:
      return 'sourcing';
  }
}

export function useAgentEvents() {
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [currentStage, setCurrentStage] = useState<AgentStage>('idle');
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingApprovals, setPendingApprovals] = useState<PendingApproval[]>([]);

  const fetchRecentEvents = useCallback(async () => {
    try {
      setError(null);
      const res = await fetch(`${API_URL}/events/recent?limit=50`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      if (data.events) {
        setEvents(data.events.reverse());
        // Set current stage from most recent event
        if (data.events.length > 0) {
          setCurrentStage(data.events[data.events.length - 1].stage);
        }
      }
    } catch (err) {
      console.error('Failed to fetch events:', err);
      setError(`Cannot connect to ${API_URL}`);
    }
  }, []);

  useEffect(() => {
    fetchRecentEvents();

    // Connect to SSE
    const eventSource = new EventSource(`${API_URL}/events/stream`);

    eventSource.onopen = () => {
      setConnected(true);
      setError(null);
    };

    eventSource.onmessage = (e) => {
      try {
        const event: AgentEvent = JSON.parse(e.data);
        setEvents((prev) => [event, ...prev].slice(0, 100));
        setCurrentStage(event.stage);

        // Handle approval_required events
        if (event.event_type === 'approval_required' && event.data) {
          const approval: PendingApproval = {
            order_id: event.order_id || `order-${Date.now()}`,
            vendor_name: event.data.vendor_name as string,
            price: event.data.price as number,
            product: event.data.product as string,
            quantity: event.data.quantity as number,
            unit: event.data.unit as string,
          };
          setPendingApprovals((prev) => {
            if (prev.some((p) => p.order_id === approval.order_id)) return prev;
            return [approval, ...prev];
          });
        }

        // Remove approval when approved
        if (event.event_type === 'order_update' && event.stage === 'approved') {
          setPendingApprovals((prev) =>
            prev.filter((p) => p.order_id !== event.order_id)
          );
        }
      } catch (err) {
        console.error('Failed to parse event:', err);
      }
    };

    eventSource.onerror = () => {
      setConnected(false);
      setError('Connection lost');
    };

    return () => eventSource.close();
  }, [fetchRecentEvents]);

  const approveOrder = async (orderId: string): Promise<boolean> => {
    try {
      const res = await fetch(`${API_URL}/orders/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_id: orderId }),
      });
      const data = await res.json();
      if (data.status === 'approved') {
        setPendingApprovals((prev) => prev.filter((p) => p.order_id !== orderId));
        return true;
      }
      return false;
    } catch (err) {
      console.error('Failed to approve order:', err);
      return false;
    }
  };

  const emitTestEvent = async () => {
    try {
      await fetch(`${API_URL}/events/test`, { method: 'POST' });
    } catch (err) {
      console.error('Failed to emit test event:', err);
    }
  };

  return {
    events,
    currentStage,
    currentPhase: stageToPhase(currentStage),
    connected,
    error,
    pendingApprovals,
    approveOrder,
    emitTestEvent,
    refresh: fetchRecentEvents,
  };
}
