'use client';
import { useEffect, useRef } from 'react';
import { usePathname } from 'next/navigation';
import { ArrowUpRightIcon } from './Icons';

// Scroll effects (parallax nuts, timeline, same-page section links) and desktop-only pointer effects (magnetic buttons, cursor ring).
export default function Interactions() {
  const ring = useRef<HTMLDivElement>(null);
  const path = usePathname();
  useEffect(() => {
    const fine = window.matchMedia('(hover:hover) and (pointer:fine)').matches;
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    let ticking = false; let raf1 = 0; let raf2 = 0;
    const speeds = Array.from(document.querySelectorAll<HTMLElement>('[data-speed]'));
    const timelines = Array.from(document.querySelectorAll<HTMLElement>('.steps'));
    const onScroll = () => { if (ticking) return; ticking = true; raf1 = requestAnimationFrame(() => {
      ticking = false; const vh = innerHeight;
      if (!reduce && innerWidth >= 1280) speeds.forEach(el => {
        const r = el.parentElement!.getBoundingClientRect(); const c = r.top + r.height / 2 - vh / 2;
        el.style.transform = `translate3d(0,${(-c * parseFloat(el.dataset.speed!)).toFixed(1)}px,0)`;
      });
      timelines.forEach(s => {
        const r = s.getBoundingClientRect(); const p = Math.min(1, Math.max(0, (vh * 0.78 - r.top) / r.height));
        s.style.setProperty('--tl', p.toFixed(3));
        const li = s.querySelectorAll('li'); li.forEach((x, i) => x.classList.toggle('on', p >= i / li.length + 0.03));
      });
    }); };
    onScroll(); addEventListener('scroll', onScroll, { passive: true }); addEventListener('resize', onScroll);
    // Links to a section on this page (such as "See our range") glide there instead of jumping.
    // Capture phase, so Next's <Link> sees the click as handled and skips its own navigation.
    const toSection = (e: MouseEvent) => {
      const a = (e.target as Element).closest<HTMLAnchorElement>('a[href*="#"]');
      if (!a || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
      const u = new URL(a.href); const el = u.pathname === location.pathname && u.hash ? document.getElementById(u.hash.slice(1)) : null;
      if (!el) return;
      e.preventDefault(); el.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
    };
    document.addEventListener('click', toSection, true);

    let cleanup = () => {};
    if (fine && !reduce) {
      let mx = 0, my = 0, x = 0, y = 0, run = false; let magnet: HTMLElement | null = null;
      const loop = () => { x += (mx - x) * 0.2; y += (my - y) * 0.2;
        if (ring.current) ring.current.style.transform = `translate3d(${x}px,${y}px,0) translate(-50%,-50%)`;
        if (Math.abs(mx - x) + Math.abs(my - y) > 0.3) raf2 = requestAnimationFrame(loop); else run = false; };
      const move = (e: PointerEvent) => {
        if (e.pointerType !== 'mouse') return; mx = e.clientX; my = e.clientY;
        ring.current?.classList.add('vis'); if (!run) { run = true; raf2 = requestAnimationFrame(loop); }
        const t = e.target as HTMLElement;
        ring.current?.classList.toggle('on', !!t.closest('.prod .imgbox'));
        const m = t.closest<HTMLElement>('.btn,.nav-cta,.soc,.ig-btn');
        if (magnet && magnet !== m) { magnet.style.translate = ''; magnet = null; }
        if (m) { const b = m.getBoundingClientRect(); m.style.translate = `${(e.clientX - b.left - b.width / 2) * 0.18}px ${(e.clientY - b.top - b.height / 2) * 0.28}px`; magnet = m; }
      };
      const leave = () => { ring.current?.classList.remove('vis'); if (magnet) { magnet.style.translate = ''; magnet = null; } };
      addEventListener('pointermove', move); document.documentElement.addEventListener('pointerleave', leave);
      cleanup = () => { removeEventListener('pointermove', move); document.documentElement.removeEventListener('pointerleave', leave); };
    }
    return () => { removeEventListener('scroll', onScroll); removeEventListener('resize', onScroll); document.removeEventListener('click', toSection, true); cancelAnimationFrame(raf1); cancelAnimationFrame(raf2); cleanup(); };
  }, [path]);
  return <div ref={ring} className="cursor-ring" aria-hidden="true"><ArrowUpRightIcon /></div>;
}
