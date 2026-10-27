export type Product = { slug: string; name: string; hindi?: string; size: string; image: string; pack: string; macro: string; blurb: string; origin: string; wa: string };
// image: AI photos for the range cards (/public/images/range). pack: pack fronts rendered from the client's pack PDFs (/public/images/packs).
// macro: nut crops from the same pack PDFs, used on the Quality page (/public/images/photos). Copy is draft. Origins are typical premium origins and need client confirmation.
export const products: Product[] = [
  { slug: 'almonds', name: 'Almonds', hindi: 'Badam', size: '250 g', image: '/images/range/almonds.webp', pack: '/images/packs/almonds.webp', macro: '/images/photos/almonds.webp', wa: 'Almonds',
    blurb: 'Clean crunch with a naturally sweet, nutty finish. Plump kernels, sorted by hand.',
    origin: 'California (USA), Kashmir (Mamra), Iran' },
  { slug: 'cashew', name: 'Cashew', hindi: 'Kaju', size: '250 g', image: '/images/range/cashew.webp', pack: '/images/packs/cashew.webp', macro: '/images/photos/cashew.webp', wa: 'Cashew',
    blurb: 'Creamy and mildly sweet, with a soft, buttery bite. Whole kernels, graded for size.',
    origin: 'Goa and Konkan coast, Kerala (Kollam), Odisha' },
  { slug: 'pistachio', name: 'Pistachio', hindi: 'Pista', size: '250 g', image: '/images/range/pistachio.webp', pack: '/images/packs/pistachio.webp', macro: '/images/photos/pistachio.webp', wa: 'Pistachio',
    blurb: 'Rich, buttery and lightly savoury, with a naturally green kernel. Picked for size and freshness.',
    origin: 'Iran, California (USA), Afghanistan' },
  { slug: 'raisins', name: 'Raisins', hindi: 'Kishmish', size: '250 g', image: '/images/range/raisins.webp', pack: '/images/packs/raisins.webp', macro: '/images/photos/raisins.webp', wa: 'Raisins',
    blurb: 'Soft, juicy and honey-sweet. Even in size and never sticky or hard.',
    origin: 'Nashik and Sangli (Maharashtra), Afghanistan' },
];
