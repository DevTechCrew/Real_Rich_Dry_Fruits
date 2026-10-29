const items = ['NOT LOUD. JUST BETTER.', 'HAND-PICKED PREMIUM DRY FRUITS', 'REAL INGREDIENTS. REAL RICH.', 'KHANDWA, MADHYA PRADESH'];
// A 3D dry fruit between the phrases (the hero's own cut-outs, so nothing extra loads): [file, height at 26 px wide]
const nuts: [string, number][] = [['almond', 17], ['cashew', 20], ['pistachio', 20], ['raisin-3', 18]];
export default function Marquee() {
  // The track holds 4 identical sets and slides by 25%, so the loop never shows a gap.
  return (
    <section className="marquee-strip" aria-label="Brand values">
      <div className="marquee-track">
        {[0, 1, 2, 3].map(k => (
          <div className="marquee-set" key={k} aria-hidden={k > 0}>
            {items.map((t, i) => <span key={t} className="marquee-item"><span>{t}</span><i><img src={`/images/photos/fly/${nuts[i][0]}.webp`} alt="" width="26" height={nuts[i][1]} loading="lazy" decoding="async" /></i></span>)}
          </div>
        ))}
      </div>
    </section>
  );
}
