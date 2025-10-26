'use client';

import { useCallback } from 'react';
import { saveSupplyRequest, getUserProfile } from '@/lib/storage';

/**
 * Hook to handle supply request submission
 * Integrates with local storage and API
 */
export function useSupplyRequest() {
  const submitRequest = useCallback(
    async (supplyType: string, quantity: number, requestText: string) => {
      const userProfile = getUserProfile();

      if (!userProfile) {
        throw new Error('User profile not found. Please provide your contact information first.');
      }

      // Save to local storage immediately
      const localRequest = saveSupplyRequest({
        supplyType,
        quantity,
        requestText,
        phoneNumber: userProfile.phoneNumber,
        address: userProfile.address,
        status: 'pending',
      });

      // Send to backend API (Claude agent integration point)
      try {
        const response = await fetch('/api/save-request', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            supplyType,
            quantity,
            requestText,
            phoneNumber: userProfile.phoneNumber,
            address: userProfile.address,
            urgency: 'high', // Can be determined by Claude agent
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to submit request to server');
        }

        const data = await response.json();
        console.log('Request submitted successfully:', data);

        return {
          success: true,
          requestId: data.requestId || localRequest.id,
          message: data.message || 'Request submitted successfully',
        };
      } catch (error) {
        console.error('Error submitting request to API:', error);
        // Request is still saved locally even if API fails
        return {
          success: true,
          requestId: localRequest.id,
          message: 'Request saved locally. Will retry submission.',
        };
      }
    },
    []
  );

  return { submitRequest };
}
