'use client';

import { useEffect, useState } from 'react';
import { getSupplyRequests, type SupplyRequest } from '@/lib/storage';
import { cn } from '@/lib/utils';

interface RequestHistoryProps {
  className?: string;
}

export function RequestHistory({ className }: RequestHistoryProps) {
  const [requests, setRequests] = useState<SupplyRequest[]>([]);

  useEffect(() => {
    // Load requests on mount
    setRequests(getSupplyRequests());

    // Refresh every 5 seconds to catch updates
    const interval = setInterval(() => {
      setRequests(getSupplyRequests());
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: SupplyRequest['status']) => {
    switch (status) {
      case 'pending':
        return 'text-yellow-600 bg-yellow-50 dark:bg-yellow-950/30';
      case 'processing':
        return 'text-blue-600 bg-blue-50 dark:bg-blue-950/30';
      case 'fulfilled':
        return 'text-green-600 bg-green-50 dark:bg-green-950/30';
      case 'cancelled':
        return 'text-gray-600 bg-gray-50 dark:bg-gray-950/30';
      default:
        return 'text-gray-600 bg-gray-50 dark:bg-gray-950/30';
    }
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  if (requests.length === 0) {
    return (
      <div className={cn('text-center py-8', className)}>
        <p className="text-muted-foreground text-sm">No requests yet</p>
        <p className="text-muted-foreground text-xs mt-1">
          Your supply requests will appear here
        </p>
      </div>
    );
  }

  return (
    <div className={cn('space-y-3', className)}>
      <h3 className="text-sm font-semibold text-foreground mb-3">Your Requests</h3>
      {requests.map((request) => (
        <div
          key={request.id}
          className="bg-card border border-border rounded-lg p-4 space-y-2"
        >
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">
                {request.supplyType}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                Quantity: {request.quantity}
              </p>
            </div>
            <span
              className={cn(
                'text-xs font-medium px-2 py-1 rounded-full whitespace-nowrap',
                getStatusColor(request.status)
              )}
            >
              {request.status}
            </span>
          </div>
          
          {request.requestText && (
            <p className="text-xs text-muted-foreground line-clamp-2">
              {request.requestText}
            </p>
          )}
          
          <div className="flex items-center justify-between pt-1 border-t border-border/50">
            <p className="text-xs text-muted-foreground">
              {formatDate(request.timestamp)}
            </p>
            <p className="text-xs text-muted-foreground">
              {request.phoneNumber}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
