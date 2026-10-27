import type { Metadata } from 'next';
import Section from '@/components/Section';
import WaButton from '@/components/WaButton';
import { InstagramIcon, MailIcon, PhoneIcon, PinIcon } from '@/components/Icons';
import { site } from '@/data/site';
import { generalMessage, waLink } from '@/lib/whatsapp';
export const metadata: Metadata = { title: 'Contact', description: 'Contact Real Rich Dry Fruits in Khandwa, Madhya Pradesh. Call, email or message on WhatsApp.' };
export default function Contact() {
  return (<>
    <Section>
      <h1>Contact</h1><hr className="rule" />
      <div className="two">
        <address style={{ fontStyle: 'normal' }}>
          <p className="ic-row"><PinIcon /><span>{site.address}</span></p>
          <p className="ic-row"><PhoneIcon /><a href={`tel:+91${site.phone}`}>{site.phone}</a></p>
          <p className="ic-row"><MailIcon /><a href={`mailto:${site.email}`}>{site.email}</a></p>
          <p className="ic-row"><InstagramIcon /><a href={site.instagram} target="_blank" rel="noopener noreferrer">{site.instagramHandle}</a></p>
          {site.hours && <p className="muted">{site.hours}</p>}
          <div className="actions">
            <WaButton href={waLink(generalMessage)} where="contact">Enquire on WhatsApp</WaButton>
            <a className="btn ghost" href={`tel:+91${site.phone}`}><PhoneIcon /> Call us</a>
          </div>
        </address>
        <iframe className="map" title="Real Rich Dry Fruits location in Khandwa" loading="lazy" referrerPolicy="no-referrer-when-downgrade"
          src={`https://www.google.com/maps?q=${encodeURIComponent(site.address)}&output=embed`} />
      </div>
    </Section>
  </>);
}
