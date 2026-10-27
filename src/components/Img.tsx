'use client';
import { useEffect, useLayoutEffect, useRef, useState } from 'react';
const useIso = typeof window !== 'undefined' ? useLayoutEffect : useEffect;
export default function Img({ src, alt, ratio = '1/1', className = '', eager = false }: { src: string; alt: string; ratio?: string; className?: string; eager?: boolean }) {
  const [bad, setBad] = useState(false);
  const [ld, setLd] = useState(false);
  const ref = useRef<HTMLImageElement>(null);
  useIso(() => { const i = ref.current; if (i && i.complete) { if (i.naturalWidth === 0) setBad(true); else setLd(true); } }, []);
  return (
    <div className={`imgbox ${className}`} style={{ aspectRatio: ratio }}>
      {bad ? <span>Photo placeholder<br />{alt}</span> : <img ref={ref} className={ld ? 'ld' : ''} src={src} alt={alt} loading={eager ? 'eager' : 'lazy'} onLoad={() => setLd(true)} onError={() => setBad(true)} />}
    </div>
  );
}
