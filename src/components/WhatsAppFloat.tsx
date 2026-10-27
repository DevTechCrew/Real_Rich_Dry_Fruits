'use client';
import { site } from '@/data/site';
import { generalMessage, waLink } from '@/lib/whatsapp';
import { track } from '@/lib/analytics';
import { PhoneIcon, WhatsAppIcon } from './Icons';
export default function WhatsAppFloat() {
  return (
    <div className="fab-stack">
      <a className="fab fab-call" href={`tel:+91${site.phone}`} aria-label="Call Real Rich" onClick={() => track('call_click', { location: 'floating' })}><PhoneIcon /></a>
      <a className="fab fab-wa" href={waLink(generalMessage)} target="_blank" rel="noopener noreferrer" aria-label="Enquire on WhatsApp" onClick={() => track('whatsapp_click', { location: 'floating' })}><WhatsAppIcon /></a>
    </div>
  );
}
