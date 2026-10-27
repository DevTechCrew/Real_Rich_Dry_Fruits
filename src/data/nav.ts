export const nav = [
  { href: '/', label: 'Home' },
  { href: '/about/', label: 'About' },
  { href: '/quality/', label: 'Quality' },
  { href: '/bulk-orders/', label: 'Bulk Orders' },
  { href: '/contact/', label: 'Contact' },
];
// No Products link in the header or footer: the range is a section on Home and "See our range" scrolls to it.
export const footerLinks = [...nav.slice(1), { href: '/faq/', label: 'FAQ' }, { href: '/privacy-policy/', label: 'Privacy Policy' }];
