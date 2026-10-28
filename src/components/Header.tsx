'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useRef, useState } from 'react';
import { nav } from '@/data/nav';
import { site } from '@/data/site';
import { generalMessage, waLink } from '@/lib/whatsapp';
import WaButton from './WaButton';
import { SparkIcon, WhatsAppIcon } from './Icons';
export default function Header() {
  const path = usePathname();
  const [open, setOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const ref = useRef<HTMLElement>(null);
  useEffect(() => {
    let raf = 0;
    const on = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => {
      const y = window.scrollY; const max = document.documentElement.scrollHeight - window.innerHeight;
      setScrolled(y > 24); ref.current?.style.setProperty('--p', String(max > 0 ? Math.min(y / max, 1) : 0));
    }); };
    on(); window.addEventListener('scroll', on, { passive: true });
    return () => { window.removeEventListener('scroll', on); cancelAnimationFrame(raf); };
  }, []);
  return (
    <header ref={ref} className={`site-header ${scrolled ? 'scrolled' : ''}`}>
      <div className="announcement"><span>PREMIUM DRY FRUITS</span><SparkIcon className="ic announcement-dot" /><span>ROOTED IN KHANDWA, MADHYA PRADESH</span></div>
      <div className="wrap nav-wrap">
        <Link href="/" className="brand" aria-label={`${site.name} home`} onClick={() => setOpen(false)}>
          <img className="brand-logo" src="/logo-mark.png" alt="" width="50" height="44" />
          <img className="brand-word" src="/logo-wordmark.png" alt="" width="126" height="17" />
        </Link>
        <button className="menu-toggle" aria-label={open ? 'Close menu' : 'Open menu'} aria-expanded={open} aria-controls="main-nav" onClick={() => setOpen(!open)}><span></span><span></span></button>
        <nav id="main-nav" className={`main-nav ${open ? 'is-open' : ''}`} aria-label="Main navigation">
          {nav.map(n => <Link key={n.href} href={n.href} className={path === n.href ? 'active' : ''} aria-current={path === n.href ? 'page' : undefined} onClick={() => setOpen(false)}>{n.label}</Link>)}
          <WaButton className="nav-cta" noIcon href={waLink(generalMessage)} where="header"><span>Message for price</span><WhatsAppIcon /></WaButton>
        </nav>
      </div>
    </header>
  );
}
