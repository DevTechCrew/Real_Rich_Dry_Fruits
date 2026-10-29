import Link from 'next/link';
import Stage3D from '@/components/Stage3D';
import Levitas from '@/components/Levitas';
import stage from '@/data/stage.json';
import type { HeroSpec } from '@/lib/stage3d';
import Marquee from '@/components/Marquee';
import Section from '@/components/Section';
import ProductRow from '@/components/ProductRow';
import { Blobs, FloatingNuts, ParallaxNut, RotatingBadge, SplitWords, Wave } from '@/components/Effects';
import WaButton from '@/components/WaButton';
import { ArrowRightIcon, InstagramIcon } from '@/components/Icons';
import { products } from '@/data/products';
import { faq } from '@/data/faq';
import { site } from '@/data/site';
import { generalMessage, waLink } from '@/lib/whatsapp';

// Icon medallions: enamel and gold, rendered in Blender (blender/render_sections.py), public/images/studio/icons.
const faqLd = { '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: faq.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) };
const why = [
  { t: 'Hand-picked', d: 'Sorted by hand, piece by piece.', icon: 'hand-picked' },
  { t: 'Sourced from origin', d: 'Bought directly from where they grow.', icon: 'origin' },
  { t: 'Premium grade only', d: 'Only the best size and quality makes the pack.', icon: 'premium' },
  { t: 'Packed fresh', d: 'Sealed to keep the crunch and aroma.', icon: 'fresh' },
];

export default function Home() {
  return (<>
    <section className="hero"><Blobs /><FloatingNuts /><div className="wrap">
      <div className="hero-copy">
        <h1 aria-label={site.tagline}><SplitWords text={site.tagline} /></h1>
        <hr className="rule" />
        <p className="lead">{site.subline}</p>
        <div className="actions">
          <a className="btn" href="#range">See our range <ArrowRightIcon /></a>
          <WaButton className="btn ghost" href={waLink(generalMessage)} where="hero">Enquire on WhatsApp</WaButton>
        </div>
      </div>
      {/* Live 3D: the real pack with the four dry fruits circling it. Turns toward the pointer; drag to spin it. */}
      <div className="hero-stage">
        <Stage3D opts={{ mode: 'hero', spec: stage as unknown as HeroSpec }} poster="/images/photos/hero-stage.webp" width={1200} height={960} eager interactWith=".hero"
          alt="A Real Rich almonds pack floating among almonds, cashews, pistachios and raisins" />
        <RotatingBadge />
      </div>
    </div></section>

    <Marquee />

    {/* The only product listing on the site, one product per row. "See our range" scrolls here */}
    <Section id="range" tone="alt" decor={<><ParallaxNut n="almond-2" side="l" top="10%" size={70} speed={0.12} /><ParallaxNut n="cashew-3" side="r" top="64%" size={66} speed={-0.1} /></>}>
      <h2>Our range</h2>
      {products.map((p, i) => <ProductRow key={p.slug} p={p} index={i} />)}
      <p style={{ marginTop: 8 }}><Link className="link" href="/bulk-orders/">Need bulk quantity? <ArrowRightIcon /></Link></p>
    </Section>

    <Wave from="almond" to="ivory" />

    <Section decor={<><ParallaxNut n="pistachio-3" side="l" top="18%" size={68} speed={0.15} /><ParallaxNut n="raisin-2" side="r" top="62%" size={56} speed={-0.12} /></>}>
      <h2>Why Real Rich</h2>
      <div className="why stagger">{why.map(w => (
        <div key={w.t}><img className="why-ic" src={`/images/studio/icons/${w.icon}.webp`} alt="" width={160} height={148} loading="lazy" decoding="async" /><h3>{w.t}</h3><p className="muted">{w.d}</p></div>
      ))}</div>
    </Section>

    <Wave from="ivory" to="espresso" />

    <Section tone="dark" center>
      <Levitas />
      {/* Confirm this wording with the client (from the Instagram post) */}
      <p className="promise stagger" style={{ margin: '0 auto' }}><span>No polish.</span><span>No colour.</span><span>No broken pieces.</span><span>No old stock.</span></p>
    </Section>

    <Wave from="espresso" to="ivory" />

    <Section>
      <div className="two" style={{ alignItems: 'center' }}>
        <div><h2>Buying in bulk?</h2><p className="muted">Retailers, shops, offices and caterers. Talk to us directly.</p>
          <p style={{ marginTop: 22 }}><Link className="btn ghost" href="/bulk-orders/">Bulk orders <ArrowRightIcon /></Link></p></div>
        <img className="studio-art bulk-art" src="/images/studio/crate.webp" alt="Real Rich packs in a wooden crate" width={900} height={573} loading="lazy" decoding="async" />
      </div>
    </Section>

    <Wave from="ivory" to="almond" />

    <Section tone="alt" center>
      <h2>On Instagram</h2>
      <a className="ig-art" href={site.instagram} target="_blank" rel="noopener noreferrer" tabIndex={-1} aria-hidden="true">
        <img src="/images/studio/flatlay.webp" alt="" width={1400} height={700} loading="lazy" decoding="async" />
      </a>
      <a className="ig-btn" href={site.instagram} target="_blank" rel="noopener noreferrer" aria-label="Follow Real Rich on Instagram"><InstagramIcon /></a>
      <p className="muted">{site.instagramHandle}</p>
    </Section>

    <Wave from="almond" to="ivory" />

    <Section center decor={<Blobs />}>
      <img className="studio-art cta-art" src="/images/studio/lineup.webp" alt="The four Real Rich packs: almonds, cashew, pistachio and raisins" width={1400} height={498} loading="lazy" decoding="async" />
      <h2>Want the price? Message us on WhatsApp.</h2>
      <div className="actions" style={{ justifyContent: 'center' }}>
        <WaButton className="btn big" href={waLink(generalMessage)} where="final_cta">Enquire on WhatsApp</WaButton>
      </div>
    </Section>

    <Wave from="ivory" to="almond" />

    {/* The FAQ lives here (there is no /faq page) */}
    <Section id="faq" tone="alt" decor={<><ParallaxNut n="cashew" side="l" top="14%" size={64} speed={0.1} /><ParallaxNut n="almond-2" side="r" top="58%" size={70} speed={-0.12} /></>}>
      <h2>Questions</h2>
      {faq.map(f => <details key={f.q}><summary>{f.q}</summary><p>{f.a}</p></details>)}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(faqLd) }} />
    </Section>
  </>);
}
