import type { Metadata } from 'next';
import Section from '@/components/Section';
import EnquiryForm from '@/components/EnquiryForm';
import WaButton from '@/components/WaButton';
import { products } from '@/data/products';
import { bulkMessage, waLink } from '@/lib/whatsapp';
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
    <Section tone="alt">
      <div className="actions" style={{ marginTop: 0 }}><WaButton className="btn big" href={waLink(bulkMessage)} where="bulk_page">WhatsApp us for bulk orders</WaButton></div>
    </Section>
    <Section>
      <h2>Or send an enquiry</h2>
      <EnquiryForm kind="bulk" />
    </Section>
  </>);
}
