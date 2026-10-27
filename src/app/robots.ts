import type { MetadataRoute } from 'next';
import { site, noindex } from '@/data/site';
export const dynamic = 'force-static';
export default function robots(): MetadataRoute.Robots {
  return noindex ? { rules: { userAgent: '*', disallow: '/' } } : { rules: { userAgent: '*', allow: '/' }, sitemap: `${site.url}/sitemap.xml` };
}
