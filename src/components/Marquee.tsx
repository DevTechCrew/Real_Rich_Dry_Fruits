const items = ['NOT LOUD. JUST BETTER.', 'HAND-PICKED PREMIUM DRY FRUITS', 'REAL INGREDIENTS. REAL RICH.', 'KHANDWA, MADHYA PRADESH'];
import { SparkIcon } from './Icons';
export default function Marquee() {
  // The track holds 4 identical sets and slides by 25%, so the loop never shows a gap.
  return (
    <section className="marquee-strip" aria-label="Brand values">
      <div className="marquee-track">
        {[0, 1, 2, 3].map(k => (
          <div className="marquee-set" key={k} aria-hidden={k > 0}>
            {items.map(t => <span key={t} className="marquee-item"><span>{t}</span><i><SparkIcon /></i></span>)}
          </div>
        ))}
      </div>
    </section>
  );
}
