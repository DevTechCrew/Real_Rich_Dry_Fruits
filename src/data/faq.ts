import { site } from './site';
// Draft answers. Do not add a delivery question until the client decides.
export const faq = [
  { q: 'How do I order?', a: 'Message us on WhatsApp with the product you want. We reply with the current price and next steps.' },
  { q: 'Why are prices not shown on the website?', a: 'Dry fruit prices change with the season, so we share today\u2019s price when you message us.' },
  { q: 'What pack sizes do you have?', a: 'Every product comes in a 250 g pack: Almonds, Cashew, Pistachio and Raisins.' },
  { q: 'Do you take bulk orders?', a: 'Yes. Retailers, shops, offices, caterers and events are welcome. Use the Bulk Orders page or message us on WhatsApp.' },
  { q: 'Where do your dry fruits come from?', a: 'We hand-pick our dry fruits and source them directly from where they grow. See the Quality page for details.' },
  { q: 'How should I store dry fruits?', a: 'Keep them in an airtight jar in a cool, dark place. Close the pack tightly after each use.' },
  { q: 'Are your products FSSAI certified?', a: `Yes. Our FSSAI licence number is ${site.fssai}.` },
  { q: 'Where are you located?', a: `We are based in Khandwa, Madhya Pradesh. ${site.address}.` },
];
