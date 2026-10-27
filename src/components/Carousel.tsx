'use client';
import { Children, useCallback, useEffect, useRef, useState } from 'react';
import { ChevronLeftIcon, ChevronRightIcon } from './Icons';

export default function Carousel({ title, children }: { title: string; children: React.ReactNode }) {
  const items = Children.toArray(children);
  const track = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(0);
  const [stops, setStops] = useState(items.length); // scroll positions (fewer than items when several fit on screen)
  const autoplay = useRef(true); // stops for good once the visitor uses the carousel
  const hovered = useRef(false);
  const visible = useRef(false);

  const step = () => {
    const t = track.current; if (!t || t.children.length < 2) return 0;
    return (t.children[1] as HTMLElement).offsetLeft - (t.children[0] as HTMLElement).offsetLeft;
  };
  const atEnd = () => { const t = track.current!; return t.scrollLeft + t.clientWidth >= t.scrollWidth - 4; };
  const go = useCallback((dir: 1 | -1) => {
    const t = track.current; if (!t) return;
    if (dir === 1 && atEnd()) t.scrollTo({ left: 0 });
    else if (dir === -1 && t.scrollLeft < 4) t.scrollTo({ left: t.scrollWidth });
    else t.scrollBy({ left: dir * step() });
  }, []);
  const user = (fn: () => void) => () => { autoplay.current = false; fn(); };

  useEffect(() => {
    const t = track.current; if (!t) return;
    let raf = 0;
    const onScroll = () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(() => {
      const s = step() || 1;
      const n = Math.max(1, Math.round((t.scrollWidth - t.clientWidth) / s) + 1);
      setStops(n);
      setActive(atEnd() ? n - 1 : Math.min(n - 1, Math.round(t.scrollLeft / s)));
    }); };
    onScroll();
    t.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    const io = new IntersectionObserver(([e]) => { visible.current = e.isIntersecting; }, { threshold: 0.4 });
    io.observe(t);
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const id = reduce ? 0 : window.setInterval(() => { if (autoplay.current && !hovered.current && visible.current && !document.hidden) go(1); }, 4500);
    return () => { t.removeEventListener('scroll', onScroll); window.removeEventListener('resize', onScroll); io.disconnect(); clearInterval(id); cancelAnimationFrame(raf); };
  }, [go, items.length]);

  const n = String(stops).padStart(2, '0');
  return (
    <div className="car" role="region" aria-roledescription="carousel" aria-label={title}
      onMouseEnter={() => { hovered.current = true; }} onMouseLeave={() => { hovered.current = false; }}>
      <div className="car-head">
        <h2>{title}</h2>
        <div className="car-ctrl">
          <span className="car-count" aria-live="polite">{String(active + 1).padStart(2, '0')} / {n}</span>
          <button className="car-btn" aria-label="Previous" onClick={user(() => go(-1))}><ChevronLeftIcon /></button>
          <button className="car-btn" aria-label="Next" onClick={user(() => go(1))}><ChevronRightIcon /></button>
        </div>
      </div>
      <div className="car-track" ref={track} onPointerDown={() => { autoplay.current = false; }}>
        {items.map((c, i) => <div className="car-item" key={i} role="group" aria-roledescription="slide" aria-label={`${i + 1} of ${items.length}`}>{c}</div>)}
      </div>
      <div className="car-dots">
        {Array.from({ length: stops }, (_, i) => <button key={i} className={`car-dot ${i === active ? 'on' : ''}`} aria-label={`Go to position ${i + 1}`} aria-current={i === active} onClick={user(() => track.current?.scrollTo({ left: i * step() }))} />)}
      </div>
    </div>
  );
}
