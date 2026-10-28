import type { Metadata, Viewport } from 'next';
import Script from 'next/script';
import './globals.css';
import './intro.css';
import Intro from '@/components/Intro';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import WhatsAppFloat from '@/components/WhatsAppFloat';
import ScrollReveal from '@/components/ScrollReveal';
import Interactions from '@/components/Interactions';
import { site, noindex } from '@/data/site';

const desc = 'Hand-picked, premium dry fruits from Khandwa, Madhya Pradesh. Almonds, Cashew, Pistachio and Raisins. Message for price.';
export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: { default: 'Premium Dry Fruits in Khandwa | Real Rich Dry Fruits', template: '%s | Real Rich Dry Fruits' },
  description: desc,
  icons: { icon: [{ url: '/favicon.ico', sizes: 'any' }, { url: '/favicon-32.png', sizes: '32x32', type: 'image/png' }, { url: '/favicon-16.png', sizes: '16x16', type: 'image/png' }], apple: '/apple-touch-icon.png' },
  robots: noindex ? { index: false, follow: false } : undefined,
  openGraph: { title: 'Real Rich Dry Fruits', description: desc, url: site.url, siteName: site.name, locale: 'en_IN', type: 'website', images: [{ url: '/og-image.png', width: 1200, height: 630 }] },
  twitter: { card: 'summary_large_image' },
};
export const viewport: Viewport = { width: 'device-width', initialScale: 1, themeColor: '#F7F2E8' };

const schema = {
  '@context': 'https://schema.org', '@type': 'LocalBusiness', name: site.name, url: site.url,
  telephone: `+91${site.phone}`, email: site.email, image: `${site.url}/og-image.png`, logo: `${site.url}/logo.png`, sameAs: [site.instagram],
  address: { '@type': 'PostalAddress', streetAddress: '241, Ward No. 38, Gali No. 5, Sindhi Colony', addressLocality: 'Khandwa', addressRegion: 'Madhya Pradesh', addressCountry: 'IN' },
  ...(site.hours ? { openingHours: site.hours } : {}),
};
const ga = process.env.NEXT_PUBLIC_GA_ID;
// Runs before the first paint: the preloader plays on a first visit, then not again for 12 hours (add ?intro to a URL
// to replay it), and never for reduced motion.
const boot = "(function(d){d.classList.add('js');try{var n=Date.now(),s=+localStorage.getItem('rr-intro')||0;if(matchMedia('(prefers-reduced-motion: reduce)').matches||(n-s<432e5&&!/[?&]intro\\b/.test(location.search))){d.classList.add('no-intro');return}localStorage.setItem('rr-intro',n);d.classList.add('intro-on','intro-hold')}catch(e){d.classList.add('no-intro')}})(document.documentElement)";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: boot }} />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=Inter:wght@400;500&display=swap" rel="stylesheet" />
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }} />
      </head>
      <body>
        <Intro />
        <Header />
        <main>{children}</main>
        <Footer />
        <WhatsAppFloat />
        <ScrollReveal />
        <Interactions />
        {ga && (<>
          <Script src={`https://www.googletagmanager.com/gtag/js?id=${ga}`} strategy="afterInteractive" />
          <Script id="ga" strategy="afterInteractive">{`window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','${ga}');`}</Script>
        </>)}
      </body>
    </html>
  );
}
