'use client';
import { useEffect } from 'react';

// Ends the preloader once the intro's own clock animation has run (intro.css, .ic-clock) and the page has loaded:
//   compose  the RR slides left and the name up beside it: the header lockup, larger, at the centre
//   glide    that lockup moves as one piece into the navbar while the paper lifts like a curtain
//   settle   the real header logo fades in under it
// Timing follows the animation, not the wall clock, so a tab opened in the background plays the intro when viewed.
// A tap or key press skips it.
const COMPOSE = 520, HOLD = 90, GLIDE = 760, SETTLE = 220;
const TOTAL = COMPOSE + HOLD + GLIDE;
const O1 = COMPOSE / TOTAL, O2 = (COMPOSE + HOLD) / TOTAL;
const OP = O2 + (1 - O2) * 0.3; // the curtain starts a little after the glide, so the logo travels over paper
const E_COMPOSE = 'cubic-bezier(.45,0,.2,1)', E_GLIDE = 'cubic-bezier(.65,0,.25,1)', E_LIFT = 'cubic-bezier(.55,0,.3,1)';
const CAP_MS = 6500; // a visible page is never held longer than this, even if rendering stalls

export default function IntroExit() {
  useEffect(() => {
    const html = document.documentElement;
    const el = document.getElementById('rr-intro');
    if (!el || !html.classList.contains('intro-on')) return;
    const finish = () => { html.classList.remove('intro-on', 'intro-hold'); html.classList.add('no-intro'); el.classList.add('ic-done'); };

    const run = (clock: Animation) => {
      const t = () => Number(clock.currentTime) || 0;
      if (t() > 4500) { finish(); return () => {}; } // the CSS fallback already hid it
      if (process.env.NODE_ENV !== 'production' && /[?&]intro=hold/.test(location.search)) return () => {}; // dev: freeze frames to review
      el.classList.add('ic-live'); // from here the exit is ours, not the CSS fallback's
      let started = false;
      let cap = 0;
      const fade = (ms: number) => el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: ms, easing: 'ease', fill: 'forwards' }).finished.then(finish);

      const dock = () => {
        const mark = el.querySelector('.ic-dock'), name = el.querySelector('.ic-name'), paper = el.querySelector('.ic-paper');
        const hm = document.querySelector('.brand-logo'), hw = document.querySelector('.brand-word');
        if (!mark || !name || !paper || !hm || !hw) return false;
        const a = mark.getBoundingClientRect(), b = name.getBoundingClientRect(), A = hm.getBoundingClientRect(), B = hw.getBoundingClientRect();
        if (!a.height || !b.height || !A.height || !B.height) return false;
        el.classList.add('is-exit');

        // The header lockup, and the same lockup lam times larger, centred where the intro sits now. Both pieces share
        // keyframe offsets and easings, so from the composed pose on they move as one rigid unit.
        const hx = (Math.min(A.left, B.left) + Math.max(A.right, B.right)) / 2, hy = (Math.min(A.top, B.top) + Math.max(A.bottom, B.bottom)) / 2;
        const lam = Math.min(2.4, (innerWidth * 0.8) / (Math.max(A.right, B.right) - Math.min(A.left, B.left)));
        const cx = (Math.min(a.left, b.left) + Math.max(a.right, b.right)) / 2, cy = (a.top + b.bottom) / 2;
        const fly = (node: Element, r: DOMRect, T: DOMRect) => {
          const k = r.width / (parseFloat(getComputedStyle(node).width) || r.width); // the stage may be scaled on short screens
          const tx = T.left + T.width / 2, ty = T.top + T.height / 2;
          const pose = (x: number, y: number, s: number) =>
            `translate(${(x - (r.left + r.width / 2)) / k}px,${(y - (r.top + r.height / 2)) / k}px) scale(${(s * T.height) / r.height})`;
          const composed = pose(cx + lam * (tx - hx), cy + lam * (ty - hy), lam);
          return node.animate([
            { transform: 'translate(0px,0px) scale(1)', easing: E_COMPOSE },
            { transform: composed, offset: O1 },
            { transform: composed, offset: O2, easing: E_GLIDE },
            { transform: pose(tx, ty, 1) },
          ], { duration: TOTAL, fill: 'forwards' });
        };
        const moves = [fly(mark, a, A), fly(name, b, B)];
        paper.animate([
          { transform: 'translateY(0)' },
          { transform: 'translateY(0)', offset: OP, easing: E_LIFT },
          { transform: 'translateY(-100%)' },
        ], { duration: TOTAL, fill: 'forwards' });
        window.setTimeout(() => html.classList.remove('intro-hold'), OP * TOTAL); // the hero enters as the curtain uncovers it

        // settle: the real header logo fades in under the landed one, then the overlay goes
        Promise.all(moves.map(m => m.finished)).then(() => {
          const show = [hm, hw].map(n => n.animate([{ opacity: 0 }, { opacity: 1 }], { duration: SETTLE, easing: 'ease', fill: 'forwards' }));
          [mark, name].forEach(n => n.animate([{ opacity: 1 }, { opacity: 0 }], { duration: SETTLE, easing: 'ease', fill: 'forwards' }));
          show[0].finished.then(() => { finish(); show.forEach(s => s.cancel()); }, finish);
        }, finish);
        return true;
      };

      const exit = (skipped = false) => {
        if (started) return;
        started = true;
        clearTimeout(cap);
        removeEventListener('pointerdown', onSkip); removeEventListener('keydown', onSkip);
        if (skipped && t() < 1500) { html.classList.remove('intro-hold'); fade(350); return; } // too early to dock: the RR is still in flight
        if (!dock()) { html.classList.remove('intro-hold'); fade(500); }
      };
      const onSkip = () => exit(true);
      const arm = () => { clearTimeout(cap); cap = window.setTimeout(() => (document.visibilityState === 'visible' ? exit() : arm()), CAP_MS); };

      const loaded = document.readyState === 'complete' ? Promise.resolve() : new Promise<void>(r => addEventListener('load', () => r(), { once: true }));
      Promise.all([clock.finished, loaded]).then(() => exit(), () => exit());
      arm();
      addEventListener('pointerdown', onSkip); addEventListener('keydown', onSkip);
      return () => { clearTimeout(cap); removeEventListener('pointerdown', onSkip); removeEventListener('keydown', onSkip); };
    };

    // Scripts can run before the stylesheet applies, so wait (briefly) for the intro's clock animation to exist.
    let waits = 0, wait = 0, off = () => {};
    const begin = () => {
      const clock = el.querySelector('.ic-clock')?.getAnimations()[0];
      if (!clock) { if (++waits > 100) finish(); else wait = window.setTimeout(begin, 50); return; }
      off = run(clock);
    };
    begin();
    return () => { clearTimeout(wait); off(); };
  }, []);
  return null;
}
