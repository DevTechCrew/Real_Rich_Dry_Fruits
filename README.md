# Real Rich Dry Fruits (Next.js static site)

    npm install
    cp .env.example .env.local   # fill in keys
    npm run dev                  # http://localhost:3000
    npm run build                # static site in /out

Edit content in src/data (site.ts, products.ts, faq.ts).
Images (replace with better versions using the same filenames):
- public/images/range: AI photos of each dry fruit for the Our range rows on Home (there is no separate products page).
- public/images/packs: pack fronts rendered unedited from the client's pack PDFs, 480 px wide WebP. When new PDFs arrive, export page 1 the same way. Never edit a pack with AI.
- public/images/origins: AI zoomed-out photos (a bowl of each dry fruit) for the origin cards on Quality, 960 x 640 WebP.
- public/images/photos: hero.webp (AI) and the floating nut cut-outs in fly/.
- public/logo*.svg/png, the favicons, icon-*.png and og-image.png: exported from the client's "REAL RICH LOGO.pdf" (Available Info) by scripts/export_logo.py. The light logo swaps the dark greens for ivory, for the dark footer.

Preloader (src/components/Intro.tsx, IntroExit.tsx, src/app/intro.css): the gold RR is struck in 3D, the name rises, then the logo docks into the header. It plays on a first visit and not again for 12 hours, never for reduced motion, and a tap or key skips it. Add ?intro to any URL to replay it. Its vector art (src/components/introArt.ts) and the nut cut-outs in public/images/intro come from scripts/gen_intro_art.py; rerun it if the logo changes.

Launch: set NEXT_PUBLIC_NOINDEX=1 on preview, remove it at launch, set NEXT_PUBLIC_SITE_URL to the real domain.

Deploy: pushing to main deploys https://real-rich.vercel.app (Vercel project real-rich, connected to this GitHub repo). Other branches get preview URLs. Vercel's Hobby plan only builds commits authored by DevTechCrew, the GitHub account linked to Vercel.
