'use client';

import { useEffect, useState } from 'react';
import { getSupplyRequests, type SupplyRequest } from '@/lib/storage';
import { cn } from '@/lib/utils';

export function ActiveRequestBanner() {
  const [latestRequest, setLatestRequest] = useState<SupplyRequest | null>(null);

  useEffect(() => {
    const updateLatestRequest = () => {
      const requests = getSupplyRequests();
      if (requests.length > 0) {
        // Get the most recent pending or processing request
        const activeRequest = requests.find(
          (r) => r.status === 'pending' || r.status === 'processing'
        );
        setLatestRequest(activeRequest || requests[0]);
      }
    };

    updateLatestRequest();
    const interval = setInterval(updateLatestRequest, 3000);

    return () => clearInterval(interval);
  }, []);

  if (!latestRequest) return null;

  const isActive = latestRequest.status === 'pending' || latestRequest.status === 'processing';

  return (
    <div
      className={cn(
        'fixed top-4 left-1/2 -translate-x-1/2 z-50 max-w-md w-full mx-4',
        'bg-card border-2 rounded-lg shadow-lg p-3',
        isActive ? 'border-yellow-500' : 'border-green-500'
      )}
    >
      <div className="flex items-start gap-3">
        <div
          className={cn(
            'flex-shrink-0 w-2 h-2 rounded-full mt-1.5',
            isActive ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'
          )}
        />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-foreground">
            {isActive ? 'Processing Request' : 'Request Completed'}
          </p>
          <p className="text-xs text-muted-foreground mt-0.5 truncate">
            {latestRequest.supplyType} (Qty: {latestRequest.quantity})
          </p>
          {isActive && (
            <p className="text-xs text-muted-foreground mt-1">
              Estimated delivery: 2-4 hours
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
