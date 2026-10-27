import Link from 'next/link';
import Section from '@/components/Section';
export default function NotFound() {
  return (
    <Section center>
      <h1>Page not found</h1><hr className="rule" />
      <p>The page you are looking for is not here.</p>
      <div className="actions" style={{ justifyContent: 'center' }}><Link className="btn" href="/">Back to home</Link><Link className="btn ghost" href="/#range">See our range</Link></div>
    </Section>
  );
}
