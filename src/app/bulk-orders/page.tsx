import type { Metadata } from 'next';
import Section from '@/components/Section';
import EnquiryForm from '@/components/EnquiryForm';
import { products } from '@/data/products';
export const metadata: Metadata = { title: 'Bulk Orders', description: 'Buying dry fruits in bulk in Khandwa and Madhya Pradesh? Enquire with Real Rich for retailers, shops, offices, caterers and events.' };
export default function Bulk() {
  return (<>
    <Section>
      <div className="two page-hero">
        <div>
          <h1>Buying in bulk? Talk to us directly.</h1><hr className="rule" />
          <h3>Who it is for</h3><p className="muted">Retailers, shops, offices, caterers and events.</p>
          <h3 style={{ marginTop: 18 }}>What we offer</h3><p className="muted">{products.map(p => p.name).join(', ')} in bulk quantities. Pricing on request.</p>
        </div>
        <img className="studio-art bulk-art" src="/images/studio/crate.webp" alt="Real Rich packs in a wooden crate" width={900} height={573} decoding="async" />
      </div>
    </Section>
    {/* The form sends its details as a WhatsApp message, so there is no separate WhatsApp button here */}
    <Section tone="alt">
      <h2>Send an enquiry</h2>
      <EnquiryForm kind="bulk" />
    </Section>
  </>);
}
