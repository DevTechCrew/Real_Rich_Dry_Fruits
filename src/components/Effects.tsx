import type { CSSProperties } from 'react';
const v = (o: Record<string, string | number>) => o as CSSProperties;

// Falls in once with a bounce, then drifts. Extras are hidden on phones (class "x").
// Single photographed nuts, cut out by blender/cutouts.py: {nut}, {nut}-2, {nut}-3 are three poses.
const NUTS: [string, number, number, number, number, boolean][] = [
  ['almond', 1, 8, 84, 0.2, true], ['cashew-2', 40, 3, 68, 0.55, false], ['pistachio', 91, 7, 78, 0.9, true],
  ['cashew', 34, 83, 76, 0.4, true], ['raisin-3', 46, 88, 58, 1.1, false], ['almond-3', 92, 78, 70, 0.7, false],
];
export function FloatingNuts() {
  return (
    <div className="fnuts" aria-hidden="true">
      {NUTS.map(([n, l, t, s, d, m], i) => (
        <span key={i} className={`fn ${m ? '' : 'x'}`} style={v({ left: `${l}%`, top: `${t}%`, width: s, '--d': `${d}s` })}>
          <img src={`/images/photos/fly/${n}.webp`} alt="" loading="lazy" style={v({ '--r': `${(i % 2 ? -1 : 1) * (8 + i * 3)}deg` })} />
        </span>
      ))}
    </div>
  );
}
export function Blobs() {
  return <div className="blobs" aria-hidden="true"><i className="b1" /><i className="b2" /><i className="b3" /></div>;
}
export function ParallaxNut({ n, side, top, size, speed }: { n: string; side: 'l' | 'r'; top: string; size: number; speed: number }) {
  return <span className={`pnut ${side}`} data-speed={speed} style={v({ top, width: size })} aria-hidden="true"><img src={`/images/photos/fly/${n}.webp`} alt="" loading="lazy" /></span>;
}
export function Wave({ from, to }: { from: 'ivory' | 'almond' | 'espresso'; to: 'ivory' | 'almond' | 'espresso' }) {
  return <div className={`wave f-${from} t-${to}`} aria-hidden="true" />;
}
export function SplitWords({ text }: { text: string }) {
  const w = text.split(' ');
  return <>{w.map((x, i) => <span key={i}><span className="sw"><span style={v({ animationDelay: `${0.15 + i * 0.13}s` })}>{x}</span></span>{i < w.length - 1 ? ' ' : ''}</span>)}</>;
}
export function RotatingBadge() {
  return (
    <div className="hero-badge" aria-hidden="true">
      <svg viewBox="0 0 120 120" className="badge-spin">
        <defs><path id="bc" d="M60 60 m-44 0 a44 44 0 1 1 88 0 a44 44 0 1 1 -88 0" /></defs>
        <circle cx="60" cy="60" r="58" fill="#F7F2E8" stroke="#B8954A" strokeWidth="1" />
        <circle cx="60" cy="60" r="31" fill="none" stroke="#B8954A" strokeOpacity=".5" strokeWidth=".8" />
        <text fontSize="9.5" letterSpacing="1.5" fill="#2B1E16" fontFamily="Inter, sans-serif"><textPath href="#bc" textLength="270" lengthAdjust="spacing">HAND-PICKED • PREMIUM DRY FRUITS • </textPath></text>
      </svg>
      <img className="badge-logo" src="/logo-mark.png" alt="" width="274" height="241" />
    </div>
  );
}
