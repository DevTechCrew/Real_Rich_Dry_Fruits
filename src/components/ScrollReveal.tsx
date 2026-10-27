'use client';
import { useEffect, useLayoutEffect } from 'react';
import { usePathname } from 'next/navigation';
const useIso = typeof window !== 'undefined' ? useLayoutEffect : useEffect;
export default function ScrollReveal() {
  const path = usePathname();
  useIso(() => {
    const els = document.querySelectorAll('.rv,.rule,.stagger');
    // Anything already on screen is shown straight away (no fade) so page changes feel instant.
    els.forEach(el => { if (el.getBoundingClientRect().top < innerHeight * 0.95) el.classList.add('in'); });
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } }), { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    els.forEach(el => { if (!el.classList.contains('in')) io.observe(el); });
    return () => io.disconnect();
  }, [path]);
  return null;
}
