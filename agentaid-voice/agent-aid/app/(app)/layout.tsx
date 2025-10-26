import { headers } from 'next/headers';
import { getAppConfig } from '@/lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

export default async function Layout({ children }: LayoutProps) {
  const hdrs = await headers();
  const { companyName, logo, logoDark } = await getAppConfig(hdrs);

  return (
    <>
      <header className="fixed top-0 right-0 z-50 p-6">
        <span className="text-muted-foreground text-xs">
          Built with{' '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://fetch.ai"
            className="hover:text-foreground transition-colors"
          >
            Fetch.ai
          </a>
          {', '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://livekit.io"
            className="hover:text-foreground transition-colors"
          >
            LiveKit
          </a>
          {' and '}
          <a
            target="_blank"
            rel="noopener noreferrer"
            href="https://claude.ai"
            className="hover:text-foreground transition-colors"
          >
            Claude
          </a>
        </span>
      </header>

      {children}
    </>
  );
}
