import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'Michael Scott Cunningham | AI Lead & Creative Systems Builder',
  description: 'Michael Scott Cunningham is an AI lead and creative systems builder working across AI adoption, multimedia, live experiences, and practical product experiments.',
  robots: { index: true, follow: true },
  alternates: { canonical: 'https://michaelscott.me/' },
  openGraph: { title: 'Michael Scott Cunningham | AI Lead & Creative Systems Builder', description: 'Turning new technology into useful workflows, memorable experiences, and things people can actually use.', type: 'website', url: 'https://michaelscott.me/', images: [{ url: 'https://michaelscott.me/og-image.png', width: 1200, height: 630, alt: 'Michael Scott Cunningham, AI lead and creative systems builder, Phoenix, Arizona' }] },
  twitter: { card: 'summary_large_image', title: 'Michael Scott Cunningham | AI Lead & Creative Systems Builder', description: 'Turning new technology into useful workflows, memorable experiences, and things people can actually use.', images: ['https://michaelscott.me/og-image.png'] },
  icons: { icon: '/favicon.svg' },
};
const personJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Person',
  name: 'Michael Scott Cunningham',
  url: 'https://michaelscott.me/',
  image: 'https://michaelscott.me/og-image.png',
  jobTitle: 'AI Lead · Event & Creative Marketing Manager',
  worksFor: { '@type': 'Organization', name: 'Mi-One Brands' },
  address: { '@type': 'PostalAddress', addressLocality: 'Phoenix', addressRegion: 'AZ', addressCountry: 'US' },
  knowsAbout: ['AI adoption', 'Workflow automation', 'Creative operations', 'Event marketing', 'Multimedia production', 'Commercial photography'],
  sameAs: ['https://www.linkedin.com/in/michael-scott-cunningham', 'https://github.com/SlySwine', 'https://x.com/SlySwine', 'https://www.instagram.com/slyswinemoto/'],
};
export default function RootLayout({children}:Readonly<{children:React.ReactNode}>){return <html lang="en"><body>{children}<script type="application/ld+json" dangerouslySetInnerHTML={{__html:JSON.stringify(personJsonLd)}} /><script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon={"{\"token\": \"e71fde36640649fcbcb2196eb20bdf13\"}"} /></body></html>}
