# Real Rich Dry Fruits (Next.js static site)

    npm install
    cp .env.example .env.local   # fill in keys
    npm run dev                  # http://localhost:3000
    npm run build                # static site in /out

Edit content in src/data (site.ts, products.ts, faq.ts).
Images (replace with better versions using the same filenames):
- public/images/range: AI photos of each dry fruit for the Our range rows on Home (there is no separate products page).
- public/images/packs: 3D renders of the 250 g stand-up pouch wearing each pack's front art exactly as the client supplied it (Blender, see below), 480 x 690 WebP with a soft contact shadow. Never edit a pack with AI.
- public/images/origins: AI zoomed-out photos (a bowl of each dry fruit) for the origin cards on Quality, 960 x 640 WebP.
- public/images/photos: hero.webp (Blender: the almonds pouch with the four dry fruits) and the floating single-nut cut-outs in fly/ (Blender, three poses of each: almond, cashew, pistachio, raisin).
- public/logo*.svg/png, the favicons and icon-*.png: exported from the client's "REAL RICH LOGO.pdf" (Available Info) by scripts/export_logo.py. The light logo swaps the dark greens for ivory, for the dark footer. og-image.png (the link preview) is the wide hero frame with logo.png on it, made by blender/export_web.py.

Blender renders (blender/, Blender 5.2, run headless; .blend files and raw renders go to ../blend-src, outside the repo):
- rr.py is the shared studio: one light rig, Khronos PBR Neutral colour (keeps the pack art's colours true), procedural almond, cashew, pistachio and raisin, linen, walnut bowl, gold spoon, the pouch, and rigid-body heaps.
- python3 blender/pack_art.py rasterises the pack PDFs (page 1, untouched) into textures; render_packs.py renders the pouches; render_fly.py the cut-outs; scenes.py the hero and share frame (scenes.py range ... renders range scenes too, not used: the AI range photos still look better).
- python3 blender/export_web.py packs fly hero og writes the site files. Run Blender as: /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P blender/<script>.py -- [options]

Preloader (src/components/Intro.tsx, IntroExit.tsx, src/app/intro.css): the gold RR is struck in 3D, the name rises, then the logo docks into the header. It plays on a first visit and not again for 12 hours, never for reduced motion, and a tap or key skips it. Add ?intro to any URL to replay it. Its vector art (src/components/introArt.ts) and the nut cut-outs in public/images/intro come from scripts/gen_intro_art.py; rerun it if the logo changes.

Launch: set NEXT_PUBLIC_NOINDEX=1 on preview, remove it at launch, set NEXT_PUBLIC_SITE_URL to the real domain.

Deploy: pushing to main deploys https://real-rich.vercel.app (Vercel project real-rich, connected to this GitHub repo). Other branches get preview URLs. Vercel's Hobby plan only builds commits authored by DevTechCrew, the GitHub account linked to Vercel.
