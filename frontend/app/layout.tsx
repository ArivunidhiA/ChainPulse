import type { Metadata } from 'next';
import './globals.css';
import { Component as BackgroundComponent } from '@/components/ui/background-components';

export const metadata: Metadata = {
  title: 'ChainPulse | DeFi Analytics',
  description: 'Real-time on-chain intelligence with a clean minimalist UI',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen text-foreground antialiased">
        <BackgroundComponent>{children}</BackgroundComponent>
      </body>
    </html>
  );
}
