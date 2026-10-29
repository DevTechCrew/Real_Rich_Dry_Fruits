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
- public/images/photos: hero-stage.webp (the poster of the live 3D hero), hero.webp (the Blender hero scene, used for the link preview) and the floating single-nut cut-outs in fly/ (photographed, three poses of each: almond, cashew, pistachio, raisin).
- public/images/studio: Blender renders for the other sections: icon medallions (icons/), the levitating dry fruits (promise-1..4, photographed), the crate of packs (bulk), the four-pack lineup (final call to action), the flat lay (Instagram), the gold monogram (About), the gold pin (Contact) and the dry fruits on the footer edge.
- public/models: the live 3D (three.js). pouch.glb is the pouch shape and art-*.webp each pack's untouched front art; the hero's dry fruits are the fly/ photographs on cards that face the camera. The hero (src/data/stage.json) and each range row show a Blender poster first and turn live once three.js has loaded (src/components/Stage3D.tsx, src/lib/stage3d.ts); they stay as images for reduced motion, without WebGL, and for the packs on touch screens. Add ?nofade in development to skip the cross-fade (for screenshots).
- public/logo*.svg/png, the favicons and icon-*.png: exported from the client's "REAL RICH LOGO.pdf" (Available Info) by scripts/export_logo.py. The light logo swaps the dark greens for ivory, for the dark footer. og-image.png (the link preview) is the wide hero frame with logo.png on it, made by blender/export_web.py.

Blender renders (blender/, Blender 5.2, run headless; .blend files and raw renders go to ../blend-src, outside the repo):
- rr.py is the shared studio: one light rig, Khronos PBR Neutral colour (keeps the pack art's colours true), almond, cashew, pistachio and raisin models, linen, walnut bowl, gold spoon, the pouch, and rigid-body heaps.
- The floating dry fruits (fly/, intro/, promise-1..4 and the hero's ring) are AI-generated studio photographs (Codex, matched to the range photos) in ../blend-src/photo/gen-*/photo.png. python3 blender/cutouts.py cuts them out with Apple's Vision subject lifting (blender/lift.swift, compiled on the first run; macOS 14+ with the command line tools), takes the backdrop out of the soft edges and writes the site files, plus PNG masters in ../blend-src/photo/cut for the hero poster.
- The dry fruits in the Blender renders (crate, lineup, flat lay, pin, footer) wear photographed skins: AI-generated macro photographs (there are no free scans of these nuts) in ../blend-src/tex, prepared by python3 blender/skins.py (evened out and made seamless) into ../blend-src/tex/final, and wrapped so the grain follows each nut (almond and pistachio-shell grooves run lengthwise and meet at the ends). Without those files rr.py falls back to its procedural skins; RR_PROCEDURAL=1 forces them.
- python3 blender/pack_art.py rasterises the pack PDFs (page 1, untouched) into textures; render_packs.py renders the pouches; render_stage.py the hero poster's pouch from src/data/stage.json (export_web.py stage paints the photographed nuts in where three.js draws them); render_sections.py the section renders; export_models.py the real-time models; scenes.py the hero scene and share frame (scenes.py range ... renders range scenes too, not used: the AI range photos still look better).
- python3 blender/export_web.py packs art stage hero og sections writes the site files. Run Blender as: /Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup -P blender/<script>.py -- [options]

Preloader (src/components/Intro.tsx, IntroExit.tsx, src/app/intro.css): the gold RR is struck in 3D, the name rises, then the logo docks into the header. It plays on every page load (reloads included, not when moving between pages inside the site), never for reduced motion, and a tap or key skips it. Its vector art (src/components/introArt.ts) and the nut cut-outs in public/images/intro come from scripts/gen_intro_art.py; rerun it if the logo changes.

Launch: set NEXT_PUBLIC_NOINDEX=1 on preview, remove it at launch, set NEXT_PUBLIC_SITE_URL to the real domain.

Deploy: pushing to main deploys https://real-rich.vercel.app (Vercel project real-rich, connected to this GitHub repo). Other branches get preview URLs. Vercel's Hobby plan only builds commits authored by DevTechCrew, the GitHub account linked to Vercel.
