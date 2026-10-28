import type { Metadata } from 'next';
import Section from '@/components/Section';
import EnquiryForm from '@/components/EnquiryForm';
import { products } from '@/data/products';
export const metadata: Metadata = { title: 'Bulk Orders', description: 'Buying dry fruits in bulk in Khandwa and Madhya Pradesh? Enquire with Real Rich for retailers, shops, offices, caterers and events.' };
export default function Bulk() {
  return (<>
    <Section>
      <h1>Buying in bulk? Talk to us directly.</h1><hr className="rule" />
      <div className="two">
        <div><h3>Who it is for</h3><p className="muted">Retailers, shops, offices, caterers and events.</p></div>
        <div><h3>What we offer</h3><p className="muted">{products.map(p => p.name).join(', ')} in bulk quantities. Pricing on request.</p></div>
      </div>
    </Section>
    {/* The form sends its details as a WhatsApp message, so there is no separate WhatsApp button here */}
    <Section tone="alt">
      <h2>Send an enquiry</h2>
      <EnquiryForm kind="bulk" />
    </Section>
  </>);
}
