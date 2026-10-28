'use client';
import { useEffect } from 'react';

// Ends the preloader: once the intro's own clock animation has run (intro.css, .ic-clock) and the page has loaded,
// the gold RR and the name fly onto the header logo while the paper dissolves, then the real logo takes over.
// Timing follows the animation, not the wall clock, so a tab opened in the background plays the intro when it is viewed.
// A tap or key press skips it.
const DOCK_MS = 950;
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

      const dock = (from: Element | null, to: Element | null) => {
        if (!from || !to) return null;
        const a = from.getBoundingClientRect(), b = to.getBoundingClientRect();
        if (!a.height || !b.height) return null;
        // the intro stage may be scaled (short screens), which would also scale the flight: correct for it
        const k = a.width / (parseFloat(getComputedStyle(from).width) || a.width);
        const dx = (b.left + b.width / 2 - (a.left + a.width / 2)) / k, dy = (b.top + b.height / 2 - (a.top + a.height / 2)) / k;
        return (from as HTMLElement).animate(
          [{ transform: 'translate(0,0) scale(1)' }, { transform: `translate(${dx}px,${dy}px) scale(${b.height / a.height})` }],
          { duration: DOCK_MS, easing: 'cubic-bezier(.72,0,.16,1)', fill: 'forwards' });
      };
      const fade = (ms: number) => el.animate([{ opacity: 1 }, { opacity: 0 }], { duration: ms, easing: 'ease', fill: 'forwards' }).finished.then(finish);

      const exit = (skipped = false) => {
        if (started) return;
        started = true;
        clearTimeout(cap);
        removeEventListener('pointerdown', onSkip); removeEventListener('keydown', onSkip);
        html.classList.remove('intro-hold'); // the hero starts its own entrance under the dissolving paper
        if (skipped && t() < 1500) { fade(350); return; } // too early to dock: the RR is still in flight
        el.classList.add('is-exit');
        const a1 = dock(el.querySelector('.ic-dock'), document.querySelector('.brand-logo'));
        const a2 = dock(el.querySelector('.ic-name'), document.querySelector('.brand-word'));
        if (!a1 || !a2) { a1?.cancel(); a2?.cancel(); fade(500); return; }
        Promise.all([a1.finished, a2.finished]).then(finish, finish);
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
