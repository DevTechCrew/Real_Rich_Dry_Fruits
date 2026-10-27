import Link from 'next/link';
import { site } from '@/data/site';
import { footerLinks } from '@/data/nav';
import { generalMessage, waLink } from '@/lib/whatsapp';
import { InstagramIcon, MailIcon, PhoneIcon, PinIcon, WhatsAppIcon } from './Icons';
import SocialLinks from './SocialLinks';
import WaButton from './WaButton';
export default function Footer() {
  return (
    <footer className="ftr">
      <div className="wrap">
        <div>
          <img className="ftr-logo" src="/logo-light.png" alt="Real Rich Dry Fruits" width="200" height="148" />
          <p style={{ marginTop: 14 }}>{site.tagline}</p>
          <small>Premium dry fruits, Khandwa, Madhya Pradesh</small>
          <SocialLinks />
        </div>
        <ul aria-label="Footer">{footerLinks.map(l => <li key={l.href}><Link href={l.href}>{l.label}</Link></li>)}</ul>
        <address style={{ fontStyle: 'normal' }}>
          <p className="ic-row"><PinIcon /><span>{site.address}</span></p>
          <p className="ic-row"><PhoneIcon /><a href={`tel:+91${site.phone}`}>{site.phone}</a></p>
          <p className="ic-row"><MailIcon /><a href={`mailto:${site.email}`}>{site.email}</a></p>
          <p className="ic-row"><WhatsAppIcon /><WaButton className="plain" noIcon href={waLink(generalMessage)} where="footer">Message on WhatsApp</WaButton></p>
          <p className="ic-row"><InstagramIcon /><a href={site.instagram} target="_blank" rel="noopener noreferrer">{site.instagramHandle}</a></p>
          <small>FSSAI Licence No. {site.fssai}</small>
        </address>
        <div className="legal">&copy; 2026 Real Rich Dry Fruits. All rights reserved.</div>
      </div>
    </footer>
  );
}
