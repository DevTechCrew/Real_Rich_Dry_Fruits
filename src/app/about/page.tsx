import type { Metadata } from 'next';
import Section from '@/components/Section';
export const metadata: Metadata = { title: 'About Us', description: 'Real Rich is a new premium dry fruit brand from Khandwa, Madhya Pradesh, building a retail chain across the state.' };
export default function About() {
  return (<>
    <Section>
      <h1>Our story</h1><hr className="rule" />
      <p className="lead">A new brand from Khandwa, started to bring truly premium dry fruits to Indian homes and businesses.</p>
    </Section>
    <Section tone="alt"><div className="two">
      <div><h2>The name</h2><p>Real Rich means rich in quality, not in show. We keep the packs simple and the dry fruits exceptional.</p></div>
      <div><h2>Our vision</h2><p>We are building a retail chain across Madhya Pradesh, starting from our home town of Khandwa.</p></div>
    </div></Section>
    <Section>
      <h2>What we stand for</h2>
      <div className="vals stagger">
        <div><h3>Quality first</h3><p className="muted">Only premium grade makes it into a Real Rich pack.</p></div>
        <div><h3>Honest sourcing</h3><p className="muted">We buy from where the dry fruits grow and say so plainly.</p></div>
        <div><h3>No shortcuts</h3><p className="muted">No polish, no added colour, no old stock.</p></div>
      </div>
    </Section>
    {/* Optional: add a shop or warehouse photo block here once the client sends one */}
  </>);
}
