import type { MetadataRoute } from 'next';
import { site } from '@/data/site';
export const dynamic = 'force-static';
export default function sitemap(): MetadataRoute.Sitemap {
  return ['', 'about/', 'quality/', 'bulk-orders/', 'contact/', 'faq/', 'privacy-policy/'].map(p => ({ url: `${site.url}/${p}` }));
}
