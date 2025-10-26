export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Emergency Relief',
  pageTitle: 'Disaster Relief Helpline',
  pageDescription: 'Request emergency supplies and assistance',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#dc2626',
  logoDark: '/plus.png',
  accentDark: '#ef4444',
  startButtonText: 'Request Help Now',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
