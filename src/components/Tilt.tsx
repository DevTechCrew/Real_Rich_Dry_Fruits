'use client';
import { useRef } from 'react';
export default function Tilt({ children }: { children: React.ReactNode }) {
  const r = useRef<HTMLDivElement>(null);
  const move = (e: React.PointerEvent) => {
    const el = r.current; if (!el || e.pointerType !== 'mouse') return;
    const b = el.getBoundingClientRect(); const x = (e.clientX - b.left) / b.width - 0.5; const y = (e.clientY - b.top) / b.height - 0.5;
    el.style.transform = `perspective(900px) rotateY(${x * 8}deg) rotateX(${-y * 8}deg) translateY(-6px)`;
  };
  const leave = () => { if (r.current) r.current.style.transform = ''; };
  return <div ref={r} className="tilt" onPointerMove={move} onPointerLeave={leave}>{children}</div>;
}
