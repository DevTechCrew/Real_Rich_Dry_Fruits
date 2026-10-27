export const nav = [
  { href: '/', label: 'Home' },
  { href: '/about/', label: 'About' },
  { href: '/#range', label: 'Products' }, // no products page: the range is a Home section
  { href: '/quality/', label: 'Quality' },
  { href: '/bulk-orders/', label: 'Bulk Orders' },
  { href: '/contact/', label: 'Contact' },
];
export const footerLinks = [...nav.slice(1), { href: '/faq/', label: 'FAQ' }, { href: '/privacy-policy/', label: 'Privacy Policy' }];
