export const nav = [
  { href: '/', label: 'Home' },
  { href: '/about/', label: 'About' },
  { href: '/quality/', label: 'Quality' },
  { href: '/bulk-orders/', label: 'Bulk Orders' },
  { href: '/contact/', label: 'Contact' },
];
// No Products or FAQ links: the range and the FAQ are sections on Home.
export const footerLinks = [...nav.slice(1), { href: '/privacy-policy/', label: 'Privacy Policy' }];
