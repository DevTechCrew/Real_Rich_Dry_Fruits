# Real Rich Dry Fruits (Next.js static site)

    npm install
    cp .env.example .env.local   # fill in keys
    npm run dev                  # http://localhost:3000
    npm run build                # static site in /out

Edit content in src/data (site.ts, products.ts, faq.ts).
Images (replace with better versions using the same filenames):
- public/images/range: AI photos of each dry fruit for the Our range cards on Home (there is no separate products page).
- public/images/packs: pack fronts rendered unedited from the client's pack PDFs, 480 px wide WebP. When new PDFs arrive, export page 1 the same way. Never edit a pack with AI.
- public/images/photos: hero.webp (AI) and nut crops from the pack PDFs (almonds, cashew, pistachio, raisins, used on Quality; mixed-nuts, used only in the Instagram strip).

Launch: set NEXT_PUBLIC_NOINDEX=1 on preview, remove it at launch, set NEXT_PUBLIC_SITE_URL to the real domain.
