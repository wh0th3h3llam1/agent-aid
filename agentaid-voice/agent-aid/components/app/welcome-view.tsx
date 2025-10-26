'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/livekit/button';
import { getUserProfile, saveUserProfile, type UserProfile } from '@/lib/storage';
import { RequestHistory } from '@/components/app/request-history';

function EmergencyIcon() {
  return (
    <svg
      width="64"
      height="64"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="text-red-600 dark:text-red-500 mb-4 size-16"
    >
      <path
        d="M12 2L2 7V12C2 16.55 5.84 20.74 12 22C18.16 20.74 22 16.55 22 12V7L12 2ZM12 11H13V17H11V11H12ZM12 9C11.45 9 11 8.55 11 8C11 7.45 11.45 7 12 7C12.55 7 13 7.45 13 8C13 8.55 12.55 9 12 9Z"
        fill="currentColor"
      />
    </svg>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [address, setAddress] = useState('');
  const [name, setName] = useState('');
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    const profile = getUserProfile();
    setUserProfile(profile);
    if (!profile) {
      setShowForm(true);
    }
  }, []);

  const handleSaveProfile = () => {
    if (!phoneNumber.trim() || !address.trim()) {
      alert('Please provide both phone number and address');
      return;
    }

    const profile: UserProfile = {
      phoneNumber: phoneNumber.trim(),
      address: address.trim(),
      name: name.trim() || undefined,
    };

    saveUserProfile(profile);
    setUserProfile(profile);
    setShowForm(false);
  };

  const handleStartCall = () => {
    if (!userProfile) {
      setShowForm(true);
      return;
    }
    onStartCall();
  };

  return (
    <div ref={ref} className="h-full overflow-y-auto">
      <section className="bg-background flex flex-col items-center justify-center text-center px-4 py-8 min-h-[60vh]">
        <EmergencyIcon />

        <h1 className="text-foreground text-2xl md:text-3xl font-bold mb-2">
          Emergency Relief Helpline
        </h1>

        <p className="text-muted-foreground max-w-prose pt-1 leading-6 font-medium mb-6">
          Request emergency supplies via voice or text
        </p>

        {showForm ? (
          <div className="w-full max-w-md space-y-4 bg-card border border-border rounded-lg p-6">
            <h2 className="text-lg font-semibold text-foreground mb-4">Your Information</h2>
            <p className="text-sm text-muted-foreground mb-4">
              We need your contact details to process your request
            </p>
            
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Name (Optional)
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Your name"
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Phone Number *
                </label>
                <input
                  type="tel"
                  value={phoneNumber}
                  onChange={(e) => setPhoneNumber(e.target.value)}
                  placeholder="+1 (555) 000-0000"
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-foreground mb-1">
                  Address *
                </label>
                <textarea
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Your full address"
                  rows={3}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary resize-none"
                  required
                />
              </div>
            </div>

            <Button
              variant="primary"
              size="lg"
              onClick={handleSaveProfile}
              className="w-full font-semibold"
            >
              Save & Continue
            </Button>
          </div>
        ) : (
          <div className="space-y-4 w-full max-w-md">
            {userProfile && (
              <div className="bg-card border border-border rounded-lg p-4 text-left">
                <p className="text-sm font-medium text-foreground">
                  {userProfile.name || 'User'}
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  {userProfile.phoneNumber}
                </p>
                <p className="text-xs text-muted-foreground">
                  {userProfile.address}
                </p>
                <button
                  onClick={() => setShowForm(true)}
                  className="text-xs text-primary hover:underline mt-2"
                >
                  Edit information
                </button>
              </div>
            )}

            <Button
              variant="primary"
              size="lg"
              onClick={handleStartCall}
              className="w-full font-semibold text-lg py-6"
            >
              {startButtonText}
            </Button>

            <button
              onClick={() => setShowHistory(!showHistory)}
              className="text-sm text-primary hover:underline font-medium"
            >
              {showHistory ? 'Hide' : 'View'} Request History
            </button>
          </div>
        )}
      </section>

      {showHistory && !showForm && (
        <section className="px-4 pb-8 max-w-2xl mx-auto">
          <RequestHistory />
        </section>
      )}

      <div className="fixed bottom-5 left-0 flex w-full items-center justify-center px-4">
        <p className="text-muted-foreground max-w-prose pt-1 text-xs leading-5 font-normal text-center">
          Available 24/7 for emergency assistance
        </p>
      </div>
    </div>
  );
};
