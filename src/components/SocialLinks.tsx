import { site } from '@/data/site';
import { generalMessage, waLink } from '@/lib/whatsapp';
import { InstagramIcon, MailIcon, PhoneIcon, WhatsAppIcon } from './Icons';
import WaButton from './WaButton';
export default function SocialLinks() {
  return (
    <div className="social">
      <WaButton className="soc" noIcon label="Message Real Rich on WhatsApp" href={waLink(generalMessage)} where="social"><WhatsAppIcon /></WaButton>
      <a className="soc" href={site.instagram} target="_blank" rel="noopener noreferrer" aria-label="Real Rich on Instagram"><InstagramIcon /></a>
      <a className="soc" href={`tel:+91${site.phone}`} aria-label="Call Real Rich"><PhoneIcon /></a>
      <a className="soc" href={`mailto:${site.email}`} aria-label="Email Real Rich"><MailIcon /></a>
    </div>
  );
}
