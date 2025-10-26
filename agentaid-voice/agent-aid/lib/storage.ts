// Local storage utilities for disaster relief app

export interface UserProfile {
  phoneNumber: string;
  address: string;
  name?: string;
}

export interface SupplyRequest {
  id: string;
  timestamp: number;
  supplyType: string;
  quantity: number;
  status: 'pending' | 'processing' | 'fulfilled' | 'cancelled';
  requestText: string;
  phoneNumber: string;
  address: string;
}

const STORAGE_KEYS = {
  USER_PROFILE: 'disaster_relief_user_profile',
  REQUESTS: 'disaster_relief_requests',
} as const;

// User Profile Management
export function getUserProfile(): UserProfile | null {
  if (typeof window === 'undefined') return null;
  
  try {
    const data = localStorage.getItem(STORAGE_KEYS.USER_PROFILE);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    console.error('Error reading user profile:', error);
    return null;
  }
}

export function saveUserProfile(profile: UserProfile): void {
  if (typeof window === 'undefined') return;
  
  try {
    localStorage.setItem(STORAGE_KEYS.USER_PROFILE, JSON.stringify(profile));
  } catch (error) {
    console.error('Error saving user profile:', error);
  }
}

export function updateUserProfile(updates: Partial<UserProfile>): void {
  const current = getUserProfile();
  if (current) {
    saveUserProfile({ ...current, ...updates });
  }
}

// Supply Requests Management
export function getSupplyRequests(): SupplyRequest[] {
  if (typeof window === 'undefined') return [];
  
  try {
    const data = localStorage.getItem(STORAGE_KEYS.REQUESTS);
    return data ? JSON.parse(data) : [];
  } catch (error) {
    console.error('Error reading supply requests:', error);
    return [];
  }
}

export function saveSupplyRequest(request: Omit<SupplyRequest, 'id' | 'timestamp'>): SupplyRequest {
  const requests = getSupplyRequests();
  
  const newRequest: SupplyRequest = {
    ...request,
    id: `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    timestamp: Date.now(),
  };
  
  requests.unshift(newRequest); // Add to beginning
  
  try {
    localStorage.setItem(STORAGE_KEYS.REQUESTS, JSON.stringify(requests));
  } catch (error) {
    console.error('Error saving supply request:', error);
  }
  
  return newRequest;
}

export function updateSupplyRequestStatus(
  requestId: string,
  status: SupplyRequest['status']
): void {
  const requests = getSupplyRequests();
  const index = requests.findIndex((r) => r.id === requestId);
  
  if (index !== -1) {
    requests[index].status = status;
    try {
      localStorage.setItem(STORAGE_KEYS.REQUESTS, JSON.stringify(requests));
    } catch (error) {
      console.error('Error updating request status:', error);
    }
  }
}

export function clearAllData(): void {
  if (typeof window === 'undefined') return;
  
  localStorage.removeItem(STORAGE_KEYS.USER_PROFILE);
  localStorage.removeItem(STORAGE_KEYS.REQUESTS);
}
