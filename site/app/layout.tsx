import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'Michael Scott Cunningham — AI Lead & Creative Systems Builder',
  description: 'Michael Scott Cunningham is an AI lead and creative systems builder working across AI adoption, multimedia, live experiences, and practical product experiments.',
  robots: { index: true, follow: true },
  alternates: { canonical: 'https://michaelscott.me/' },
  openGraph: { title: 'Michael Scott Cunningham — AI Lead & Creative Systems Builder', description: 'Turning new technology into useful workflows, memorable experiences, and things people can actually use.', type: 'website', url: 'https://michaelscott.me/' },
  icons: { icon: '/favicon.svg' },
};
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body>{children}<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon={"{\"token\": \"e71fde36640649fcbcb2196eb20bdf13\"}"} /></body></html>}
