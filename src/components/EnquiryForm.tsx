'use client';
import { useState } from 'react';
import { products } from '@/data/products';
import { track } from '@/lib/analytics';
import { bulkMessage, waLink } from '@/lib/whatsapp';
import { WhatsAppIcon } from './Icons';

// Sends the enquiry as a prefilled WhatsApp message to Real Rich (no form service or email).
export default function EnquiryForm({ kind }: { kind: 'bulk' | 'contact' }) {
  const [sent, setSent] = useState('');
  function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const fd = new FormData(e.currentTarget);
    const v = (k: string) => String(fd.get(k) || '').trim();
    const picked = fd.getAll('product').join(', ');
    const text = [
      kind === 'bulk' ? bulkMessage : 'Hi Real Rich, I have an enquiry.',
      `Name: ${v('name')}`,
      v('business') && `Business: ${v('business')}`,
      v('city') && `City: ${v('city')}`,
      `Phone: ${v('phone')}`,
      picked && `Products: ${picked}`,
      v('quantity_kg') && `Quantity: ${v('quantity_kg')} kg`,
      v('message') && `Message: ${v('message')}`,
    ].filter(Boolean).join('\n');
    const url = waLink(text);
    track('form_submit', { form: kind, channel: 'whatsapp' });
    // A new tab keeps the site open; if the browser blocks it, open WhatsApp in this tab.
    const w = window.open(url, '_blank');
    if (w) w.opener = null; else location.href = url;
    setSent(url);
  }
  if (sent)
    return (
      <div className="thanks" role="status">
        <h3>Almost done.</h3>
        <p>Your enquiry is ready in WhatsApp. Press send there and we will reply on WhatsApp.</p>
        <a className="btn" href={sent} target="_blank" rel="noopener noreferrer"><WhatsAppIcon />Open WhatsApp again</a>
      </div>
    );
  const bulk = kind === 'bulk';
  return (
    <form onSubmit={onSubmit}>
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
      <button className="btn" type="submit"><WhatsAppIcon />Send enquiry</button>
    </form>
  );
}
