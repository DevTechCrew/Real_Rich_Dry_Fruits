import type { Metadata } from 'next';
import Section from '@/components/Section';
import { site } from '@/data/site';
export const metadata: Metadata = { title: 'Privacy Policy', description: 'How Real Rich Dry Fruits handles the details you share through our enquiry forms.' };
export default function Privacy() {
  return (
    <Section>
      <h1>Privacy Policy</h1><hr className="rule" />
      <p className="muted">Last updated: October 2026</p>
      <h3 style={{ marginTop: 28 }}>What we collect</h3>
      <p>When you send an enquiry we collect the name, city, phone number, business name, products, quantity and message you enter.</p>
      <h3 style={{ marginTop: 28 }}>How we use it</h3>
      <p>We use these details only to reply to your enquiry. We do not sell your details. When you press Send enquiry, they open in WhatsApp and reach us only when you send that message.</p>
      <h3 style={{ marginTop: 28 }}>Analytics</h3>
      <p>We use Google Analytics to count visits and WhatsApp or form clicks. It does not tell us who you are.</p>
      <h3 style={{ marginTop: 28 }}>Your choices</h3>
      <p>To ask us to delete your details, write to <a href={`mailto:${site.email}`}>{site.email}</a>.</p>
    </Section>
  );
}
