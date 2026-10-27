import type { Metadata } from 'next';
import Section from '@/components/Section';
import { faq } from '@/data/faq';
export const metadata: Metadata = { title: 'FAQ', description: 'Answers about ordering, pack sizes, bulk orders, storage and FSSAI for Real Rich Dry Fruits.' };
export default function Faq() {
  const ld = { '@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: faq.map(f => ({ '@type': 'Question', name: f.q, acceptedAnswer: { '@type': 'Answer', text: f.a } })) };
  return (
    <Section>
      <h1>Questions</h1><hr className="rule" />
      {faq.map(f => <details key={f.q}><summary>{f.q}</summary><p>{f.a}</p></details>)}
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(ld) }} />
    </Section>
  );
}
