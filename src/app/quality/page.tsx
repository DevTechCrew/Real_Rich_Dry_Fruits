import type { Metadata } from 'next';
import Section from '@/components/Section';
import Img from '@/components/Img';
import { products } from '@/data/products';
import { site } from '@/data/site';
export const metadata: Metadata = { title: 'Quality and Sourcing', description: 'Hand-picked and sourced directly from where they grow. Learn how Real Rich selects its dry fruits.' };
const steps = [
  ['Sourced at origin', 'We buy directly from the regions where each dry fruit grows.'],
  ['Hand-sorted', 'Every batch is sorted by hand to remove broken and discoloured pieces.'],
  ['Graded by size', 'Only uniform, premium-grade pieces are kept.'],
  ['Packed fresh', 'Sealed in 250 g packs to hold the flavour.'],
]; // confirm steps with client
export default function Quality() {
  return (<>
    <Section>
      <h1>Quality</h1><hr className="rule" />
      <p className="lead">Hand-picked and sourced directly from where they grow.</p>
    </Section>
    <Section tone="alt">
      <h2>Where our dry fruits come from</h2>
      {!site.originsConfirmed && <p className="note">Draft for client confirmation. These are typical premium origins. Remove this note and set originsConfirmed to true in data/site.ts after approval.</p>}
      <div className="grid4 stagger">{products.map(p => <div key={p.slug}><Img src={p.originPhoto} alt={`${p.name} in a wooden bowl`} ratio="3/2" /><h3 style={{ marginTop: 14 }}>{p.name}</h3><hr className="rule" /><p className="muted">{p.origin}</p></div>)}</div>
    </Section>
    <Section>
      <h2>How we pick</h2>
      <ol className="steps stagger">{steps.map(([t, d]) => <li key={t}><div><h3>{t}</h3><p className="muted">{d}</p></div></li>)}</ol>
    </Section>
    <Section tone="dark">
      <h2>Food safety</h2>
      <p>We operate under an FSSAI licence. Licence No. {site.fssai}.</p>
    </Section>
  </>);
}
