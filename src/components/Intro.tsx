'use client';
import { GLYPHS, MARK, MARK_VB, NAME, NAME_VB, RULES, TAG, TAG_VB, TM } from './introArt';
import IntroExit from './IntroExit';

// First-visit preloader, "The Gilded Seal": a gold ring traces itself, three dry fruits orbit it in 3D, the RR is
// struck in gold (an extruded stack of the real logo paths), the name rises, then the logo docks into the header.
// It plays on CSS alone (intro.css). The head script in layout.tsx decides before the first paint whether it shows;
// IntroExit only runs the exit. A client component on purpose: the artwork then sits in one cached script instead of
// being repeated in every page's navigation data. It is still server-rendered, so it shows in the first paint.

const LAYERS = 12; // depth slices behind the gold face
const mix = (a: string, b: string, t: number) => '#' + [0, 2, 4].map(i => Math.round(parseInt(a.slice(1 + i, 3 + i), 16) * (1 - t) + parseInt(b.slice(1 + i, 3 + i), 16) * t).toString(16).padStart(2, '0')).join('');
const NUTS = [['almond', 0], ['pistachio', 120], ['raisin', 240]] as const;
const RING_TEXT = 'HAND-PICKED  •  PREMIUM DRY FRUITS  •  KHANDWA, MADHYA PRADESH  •  ';

export default function Intro() {
  return (
    <div id="rr-intro" className="intro" aria-hidden="true">
      <svg className="ic-defs" width="0" height="0" focusable="false">
        <defs>
          {MARK.map((d, i) => <path key={i} id={`ic-p${i}`} d={d} />)}
          <g id="ic-mark">{MARK.map((_, i) => <use key={i} href={`#ic-p${i}`} />)}</g>
          <clipPath id="ic-clip">{MARK.map((_, i) => <use key={i} href={`#ic-p${i}`} />)}</clipPath>
          {Object.entries(GLYPHS).map(([id, d]) => <path key={id} id={`ic-${id}`} d={d} />)}
          <linearGradient id="ic-foil" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#FBE7AE" /><stop offset=".2" stopColor="#EDB54B" /><stop offset=".42" stopColor="#E09E27" />
            <stop offset=".56" stopColor="#F5CB6C" /><stop offset=".74" stopColor="#C98117" /><stop offset=".9" stopColor="#E3A23A" /><stop offset="1" stopColor="#B8741A" />
          </linearGradient>
          <linearGradient id="ic-shine" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0" stopColor="#FFF6DC" stopOpacity="0" /><stop offset=".45" stopColor="#FFF6DC" stopOpacity=".7" /><stop offset=".5" stopColor="#FFFFFF" stopOpacity="1" /><stop offset=".55" stopColor="#FFF6DC" stopOpacity=".7" /><stop offset="1" stopColor="#FFF6DC" stopOpacity="0" />
          </linearGradient>
          <path id="ic-tp" d="M150 150m-127 0a127 127 0 1 1 254 0a127 127 0 1 1-254 0" />
        </defs>
      </svg>

      <div className="ic-paper" />
      <div className="ic-stage">
        <div className="ic-seal">
          <div className="ic-ripple" /><div className="ic-ripple ic-ripple2" /><div className="ic-press" />
          <svg className="ic-ring" viewBox="0 0 300 300">
            <circle className="ic-ring1" cx="150" cy="150" r="146" />
            <circle className="ic-ring2" cx="150" cy="150" r="108" />
            <g className="ic-ringtext"><text><textPath href="#ic-tp" textLength="790" lengthAdjust="spacing">{RING_TEXT}</textPath></text></g>
          </svg>
          <div className="ic-world">
            <div className="ic-orbit">
              {NUTS.map(([n, a]) => (
                <div key={n} className="ic-nut" style={{ '--a': `${a}deg` } as React.CSSProperties}>
                  <div className="ic-nut-r"><div className="ic-nut-b"><div className="ic-nut-c">
                    <img src={`/images/intro/${n}.webp`} alt="" width="150" height="95" loading="lazy" decoding="async" />
                  </div></div></div>
                </div>
              ))}
            </div>
            <div className="ic-dock">
              <div className="ic-coin">
                {Array.from({ length: LAYERS }, (_, k) => LAYERS - k).map(i => (
                  <svg key={i} className="ic-layer" viewBox={MARK_VB} style={{ '--i': i, fill: mix('#B06A12', '#5A3507', (i - 1) / (LAYERS - 1)) } as React.CSSProperties}><use href="#ic-mark" /></svg>
                ))}
                <svg className="ic-face" viewBox={MARK_VB}>
                  <use href="#ic-mark" fill="url(#ic-foil)" />
                  <g clipPath="url(#ic-clip)"><rect className="ic-glint" x="40" y="20" width="44" height="150" fill="url(#ic-shine)" /></g>
                  <use className="ic-flat" href="#ic-mark" fill="#E09E27" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div className="ic-lockup">
          <svg className="ic-name" viewBox={NAME_VB}>
            {NAME.map(([g, m], k) => <g key={k} className="ic-l" style={{ '--k': k } as React.CSSProperties}><use href={`#ic-${g}`} transform={m} /></g>)}
            <g className="ic-tm">{TM.map((d, i) => <path key={i} d={d} />)}</g>
          </svg>
          <svg className="ic-tag" viewBox={TAG_VB}>
            <path className="ic-rule ic-rule-l" d={RULES[0]} /><path className="ic-rule ic-rule-r" d={RULES[1]} />
            {TAG.map(([g, m], k) => <g key={k} className="ic-tl" style={{ '--k': Math.abs(k - (TAG.length - 1) / 2) } as React.CSSProperties}><use href={`#ic-${g}`} transform={m} /></g>)}
          </svg>
        </div>
      </div>
      <i className="ic-clock" />
      <IntroExit />
    </div>
  );
}
