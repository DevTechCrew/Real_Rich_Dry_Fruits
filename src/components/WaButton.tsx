'use client';
import { track } from '@/lib/analytics';
import { WhatsAppIcon } from './Icons';
export default function WaButton({ href, children, where, className = 'btn', label, noIcon = false }: { href: string; children: React.ReactNode; where: string; className?: string; label?: string; noIcon?: boolean }) {
  return <a className={className} href={href} target="_blank" rel="noopener noreferrer" aria-label={label} onClick={() => track('whatsapp_click', { location: where })}>{!noIcon && <WhatsAppIcon />}{children}</a>;
}
