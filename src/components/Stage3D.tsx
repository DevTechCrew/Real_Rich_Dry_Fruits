'use client';
import { useEffect, useRef, useState } from 'react';
import type { StageOptions } from '@/lib/stage3d';

// A Blender poster image that turns into live 3D (src/lib/stage3d.ts) once three.js has loaded: on demand, after the
// preloader, near the viewport. The poster stays for reduced motion, no WebGL, and (for packs) touch screens.
export default function Stage3D({ opts, poster, alt, width, height, className = '', eager = false, interactWith, desktopOnly = false }: {
  opts: StageOptions; poster: string; alt: string; width: number; height: number; className?: string; eager?: boolean;
  interactWith?: string; desktopOnly?: boolean;
}) {
  const box = useRef<HTMLDivElement>(null);
  const cv = useRef<HTMLCanvasElement>(null);
  const [live, setLive] = useState(false);
  const [done, setDone] = useState(false);
  const [instant, setInstant] = useState(false);
  useEffect(() => {
    const el = box.current, canvas = cv.current;
    if (!el || !canvas || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (desktopOnly && !matchMedia('(hover: hover) and (pointer: fine) and (min-width: 880px)').matches) return;
    let dead = false, stop = () => {}, io: IntersectionObserver | null = null, mo: MutationObserver | null = null;
    const start = () => {
      io = new IntersectionObserver(([e]) => {
        if (!e.isIntersecting) return;
        io?.disconnect();
        import('@/lib/stage3d').then(m => {
          if (dead) return;
          stop = m.mountStage(canvas, opts, {
            interactEl: (interactWith && el.closest<HTMLElement>(interactWith)) || el,
            onReady: () => {
              // the poster goes only once the canvas has really finished fading in (never on a timer: a throttled tab could stall the fade)
              const end = (e: TransitionEvent) => { if (e.propertyName === 'opacity' && !dead) { canvas.removeEventListener('transitionend', end); setDone(true); } };
              canvas.addEventListener('transitionend', end);
              if (process.env.NODE_ENV !== 'production' && /[?&]nofade/.test(location.search)) { setInstant(true); setDone(true); } // dev: screenshots
              setLive(true);
            },
            onLost: () => { setLive(false); setDone(false); },
          });
        }).catch(() => {});
      }, { rootMargin: '300px' });
      io.observe(el);
    };
    const html = document.documentElement;                  // wait for the preloader, so the two never compete
    if (html.classList.contains('intro-on')) {
      mo = new MutationObserver(() => { if (!html.classList.contains('intro-on')) { mo?.disconnect(); start(); } });
      mo.observe(html, { attributes: true, attributeFilter: ['class'] });
    } else start();
    return () => { dead = true; io?.disconnect(); mo?.disconnect(); stop(); };
  }, [opts, interactWith, desktopOnly]);
  return (
    <div ref={box} className={`stage ${className}${live ? ' live' : ''}${done ? ' done' : ''}${instant ? ' instant' : ''}`}>
      <img className="stage-poster" src={poster} alt={alt} width={width} height={height} loading={eager ? 'eager' : 'lazy'} decoding="async" />
      <canvas ref={cv} className="stage-gl" aria-hidden="true" />
    </div>
  );
}
