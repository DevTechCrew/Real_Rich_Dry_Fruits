import Link from 'next/link';
import Img from '@/components/Img';
import Marquee from '@/components/Marquee';
import Section from '@/components/Section';
import ProductCard from '@/components/ProductCard';
import Carousel from '@/components/Carousel';
import { Blobs, FloatingNuts, ParallaxNut, RotatingBadge, SplitWords, Wave } from '@/components/Effects';
import WaButton from '@/components/WaButton';
import { ArrowRightIcon, InstagramIcon } from '@/components/Icons';
import { products } from '@/data/products';
import { site } from '@/data/site';
import { generalMessage, waLink } from '@/lib/whatsapp';

// Thin line icons (24 grid). pathLength lets CSS draw them in.
const why = [
  { t: 'Hand-picked', d: 'Sorted by hand, piece by piece.', i: <><path pathLength={1} d="M12 3c4 3 6 7 6 11a6 6 0 0 1-12 0c0-4 2-8 6-11Z" /><path pathLength={1} d="m9 14 2 2 4-4" /></> },
  { t: 'Sourced from origin', d: 'Bought directly from where they grow.', i: <><circle pathLength={1} cx="12" cy="12" r="9" /><path pathLength={1} d="M3 12h18M12 3c-3.500 4-3.500 14 0 18M12 3c3.500 4 3.500 14 0 18" /></> },
  { t: 'Premium grade only', d: 'Only the best size and quality makes the pack.', i: <><circle pathLength={1} cx="12" cy="9" r="5.500" /><path pathLength={1} d="m8.500 13.500-1.500 7.500 5-3 5 3-1.500-7.500" /></> },
  { t: 'Packed fresh', d: 'Sealed to keep the crunch and aroma.', i: <><path pathLength={1} d="M7 4h10l2 3v12a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V7l2-3Z" /><path pathLength={1} d="M5 7h14M9 12.500c1.500-1.500 4.500-1.500 6 0" /></> },
];
const tiles = ['almonds', 'mixed-nuts', 'pistachio', 'raisins'];

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
      <div className="levitate">
        <Img src="/images/photos/hero.webp" alt="Cashews, almonds, pistachios and raisins on ivory linen" ratio="3/2" className="hero-img" eager />
        <span className="levitate-shadow" aria-hidden="true" />
        <RotatingBadge />
      </div>
    </div></section>

    <Marquee />

    {/* The only product listing on the site: "See our range" and the Products menu link scroll here */}
    <Section id="range" tone="alt" decor={<><ParallaxNut n="almond" side="l" top="10%" size={70} speed={0.12} /><ParallaxNut n="raisin" side="r" top="64%" size={62} speed={-0.1} /></>}>
      <Carousel title="Our range">{products.map((p, i) => <ProductCard key={p.slug} p={p} index={i} />)}</Carousel>
      <p style={{ marginTop: 8 }}><Link className="link" href="/bulk-orders/">Need bulk quantity? <ArrowRightIcon /></Link></p>
    </Section>

    <Wave from="almond" to="ivory" />

    <Section decor={<><ParallaxNut n="pistachio" side="l" top="18%" size={68} speed={0.15} /><ParallaxNut n="almond" side="r" top="62%" size={72} speed={-0.12} /></>}>
      <h2>Why Real Rich</h2>
      <div className="why stagger">{why.map(w => (
        <div key={w.t}><svg viewBox="0 0 24 24" aria-hidden="true">{w.i}</svg><h3>{w.t}</h3><p className="muted">{w.d}</p></div>
      ))}</div>
    </Section>

    <Wave from="ivory" to="espresso" />

    <Section tone="dark" center>
      {/* Confirm this wording with the client (from the Instagram post) */}
      <p className="promise stagger" style={{ margin: '0 auto' }}><span>No polish.</span><span>No colour.</span><span>No broken pieces.</span><span>No old stock.</span></p>
    </Section>

    <Wave from="espresso" to="ivory" />

    <Section>
      <div className="two" style={{ alignItems: 'center' }}>
        <div><h2>Buying in bulk?</h2><p className="muted">Retailers, shops, offices and caterers. Talk to us directly.</p></div>
        <div><Link className="btn ghost" href="/bulk-orders/">Bulk orders <ArrowRightIcon /></Link></div>
      </div>
    </Section>

    <Wave from="ivory" to="almond" />

    <Section tone="alt">
      <h2>On Instagram</h2>
      <p style={{ margin: '4px 0 8px' }}><a className="btn ghost" href={site.instagram} target="_blank" rel="noopener noreferrer"><InstagramIcon /> Follow {site.instagramHandle}</a></p>
      {/* Static tiles linking to the profile. Swap in real post images when available. */}
      <div className="tiles stagger">{tiles.map(s => (
        <a key={s} href={site.instagram} target="_blank" rel="noopener noreferrer" aria-label={`Real Rich on Instagram: ${s.replace('-', ' ')}`}>
          <Img src={`/images/photos/${s}.webp`} alt={`${s.replace('-', ' ')}`} />
          <span className="tile-badge" aria-hidden="true"><InstagramIcon /></span>
          <span className="tile-ic" aria-hidden="true"><InstagramIcon /></span>
        </a>
      ))}</div>
    </Section>

    <Wave from="almond" to="ivory" />

    <Section center decor={<Blobs />}>
      <h2>Want the price? Message us on WhatsApp.</h2>
      <div className="actions" style={{ justifyContent: 'center' }}>
        <WaButton className="btn big" href={waLink(generalMessage)} where="final_cta">Enquire on WhatsApp</WaButton>
      </div>
    </Section>
  </>);
}
