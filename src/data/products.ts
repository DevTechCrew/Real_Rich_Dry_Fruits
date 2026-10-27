export type Product = { slug: string; name: string; hindi?: string; size: string; image: string; pack: string; originPhoto: string; blurb: string; origin: string; wa: string };
// image: AI photos for the range cards (/public/images/range). pack: pack fronts rendered from the client's pack PDFs (/public/images/packs).
// originPhoto: AI zoomed-out photos for the origin cards on Quality (/public/images/origins). Copy is draft. Origins were confirmed in the Oct 2026 change request.
export const products: Product[] = [
  { slug: 'almonds', name: 'Almonds', hindi: 'Badam', size: '250 g', image: '/images/range/almonds.webp', pack: '/images/packs/almonds.webp', originPhoto: '/images/origins/almonds.webp', wa: 'Almonds',
    blurb: 'Clean crunch with a naturally sweet, nutty finish. Plump kernels, sorted by hand.',
    origin: 'California (USA), Kashmir (Mamra), Iran' },
  { slug: 'cashew', name: 'Cashew', hindi: 'Kaju', size: '250 g', image: '/images/range/cashew.webp', pack: '/images/packs/cashew.webp', originPhoto: '/images/origins/cashew.webp', wa: 'Cashew',
    blurb: 'Creamy and mildly sweet, with a soft, buttery bite. Whole kernels, graded for size.',
    origin: 'Goa and Konkan coast, Kerala (Kollam), Odisha' },
  { slug: 'pistachio', name: 'Pistachio', hindi: 'Pista', size: '250 g', image: '/images/range/pistachio.webp', pack: '/images/packs/pistachio.webp', originPhoto: '/images/origins/pistachio.webp', wa: 'Pistachio',
    blurb: 'Rich, buttery and lightly savoury, with a naturally green kernel. Picked for size and freshness.',
    origin: 'Iran, California (USA), Afghanistan' },
  { slug: 'raisins', name: 'Raisins', hindi: 'Kishmish', size: '250 g', image: '/images/range/raisins.webp', pack: '/images/packs/raisins.webp', originPhoto: '/images/origins/raisins.webp', wa: 'Raisins',
    blurb: 'Soft, juicy and honey-sweet. Even in size and never sticky or hard.',
    origin: 'Nashik and Sangli (Maharashtra), Afghanistan' },
];
