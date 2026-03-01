import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'RTI Voice Assistant',
  description: 'Accessible RTI filing assistant for visually impaired users',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
