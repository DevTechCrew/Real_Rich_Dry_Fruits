'use client';
import { useState } from 'react';
import { products } from '@/data/products';
import { track } from '@/lib/analytics';

export default function EnquiryForm({ kind }: { kind: 'bulk' | 'contact' }) {
  const [state, setState] = useState<'idle' | 'sending' | 'done' | 'error'>('idle');
  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    if (fd.get('botcheck')) return; // honeypot
    const picked = fd.getAll('product');
    fd.delete('product');
    if (picked.length) fd.set('products', picked.join(', '));
    fd.set('access_key', process.env.NEXT_PUBLIC_FORM_KEY || '');
    if (process.env.NEXT_PUBLIC_FORM_CC) fd.set('ccemail', process.env.NEXT_PUBLIC_FORM_CC);
    fd.set('subject', `Real Rich website: ${kind === 'bulk' ? 'bulk order' : 'contact'} enquiry`);
    fd.set('from_name', 'Real Rich website');
    setState('sending');
    try {
      const r = await fetch('https://api.web3forms.com/submit', { method: 'POST', body: fd });
      const j = await r.json();
      if (j.success) { track('form_submit', { form: kind }); setState('done'); } else setState('error');
    } catch { setState('error'); }
  }
  if (state === 'done')
    return <div className="thanks" role="status"><h3>Thank you.</h3><p>We have your enquiry and will message you on the phone number you shared.</p></div>;
  const bulk = kind === 'bulk';
  return (
    <form onSubmit={onSubmit}>
      <div className="hp" aria-hidden="true"><label>Leave empty<input type="text" name="botcheck" tabIndex={-1} autoComplete="off" /></label></div>
      <div><label htmlFor={`n-${kind}`}>Name</label><input id={`n-${kind}`} type="text" name="name" required autoComplete="name" /></div>
      {bulk && <div><label htmlFor="biz">Business name (optional)</label><input id="biz" type="text" name="business" autoComplete="organization" /></div>}
      <div><label htmlFor={`c-${kind}`}>City</label><input id={`c-${kind}`} type="text" name="city" required={bulk} autoComplete="address-level2" /></div>
      <div><label htmlFor={`p-${kind}`}>Phone</label><input id={`p-${kind}`} type="tel" name="phone" required inputMode="tel" pattern="[0-9+\s\-]{10,15}" autoComplete="tel" /></div>
      {bulk && <>
        <fieldset><legend>Products</legend><div className="checks">
          {products.map(p => <label key={p.slug}><input type="checkbox" name="product" value={p.name} />{p.name}</label>)}
        </div></fieldset>
        <div><label htmlFor="qty">Approximate quantity (kg)</label><input id="qty" type="number" name="quantity_kg" min="1" inputMode="numeric" /></div>
      </>}
      <div><label htmlFor={`m-${kind}`}>Message</label><textarea id={`m-${kind}`} name="message" /></div>
      {state === 'error' && <p className="err" role="alert">We could not send this. Please try again or message us on WhatsApp.</p>}
      <button className="btn" type="submit" disabled={state === 'sending'}>{state === 'sending' ? 'Sending' : 'Send enquiry'}</button>
    </form>
  );
}
