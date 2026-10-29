import type { CSSProperties } from 'react';
// The four dry fruits levitating, photographed rim-lit on black (blender/cutouts.py): one slice per nut, so each floats on its own beat.
const slices: [number, number][] = [[391, 276], [365, 276], [364, 276], [365, 276]];
const total = slices.reduce((a, [w]) => a + w, 0);
export default function Levitas() {
  return (
    <div className="levitas" aria-hidden="true">{slices.map(([w, h], i) => (
      <img key={i} src={`/images/studio/promise-${i + 1}.webp`} alt="" width={w} height={h} loading="lazy" decoding="async"
        style={{ width: `${(w / total) * 100}%`, '--i': i } as CSSProperties} />
    ))}</div>
  );
}
