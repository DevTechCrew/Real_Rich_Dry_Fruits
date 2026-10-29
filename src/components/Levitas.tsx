import type { CSSProperties } from 'react';
// The four dry fruits levitating (blender/render_sections.py, promise): one slice per nut, so each floats on its own beat.
const slices: [number, number][] = [[347, 279], [375, 279], [341, 279], [337, 279]];
const total = slices.reduce((a, [w]) => a + w, 0);
export default function Levitas() {
  return (
    <div className="levitas" aria-hidden="true">{slices.map(([w, h], i) => (
      <img key={i} src={`/images/studio/promise-${i + 1}.webp`} alt="" width={w} height={h} loading="lazy" decoding="async"
        style={{ width: `${(w / total) * 100}%`, '--i': i } as CSSProperties} />
    ))}</div>
  );
}
