import { animate, stagger } from "animejs";
import { useEffect, useRef, useState } from "react";
import { prefersReducedMotion } from "../hooks/motion";

const MIN_MS = 1100; // keep the intro on screen long enough to read, never a flash
const WORD = "GridPulse";

/** Config-2026-style kinetic loading screen. Stays until data is `ready` AND the
 *  intro has played for MIN_MS, then wipes up to reveal the app. */
export function Splash({ ready, onDone }: { ready: boolean; onDone: () => void }) {
  const root = useRef<HTMLDivElement>(null);
  const [minDone, setMinDone] = useState(false);
  const exiting = useRef(false);

  // Intro sequence on mount.
  useEffect(() => {
    const timer = window.setTimeout(() => setMinDone(true), MIN_MS);
    if (prefersReducedMotion() || !root.current) {
      return () => window.clearTimeout(timer);
    }
    const el = root.current;
    animate(el.querySelectorAll<HTMLElement>(".splash-logo"), {
      opacity: [0, 1],
      scale: [0.6, 1],
      duration: 600,
      ease: "outBack",
    });
    animate(el.querySelectorAll<HTMLElement>(".splash-word span"), {
      opacity: [0, 1],
      translateY: [26, 0],
      delay: stagger(45, { start: 200 }),
      duration: 560,
      ease: "outExpo",
    });
    animate(el.querySelectorAll<HTMLElement>(".splash-fill"), {
      scaleX: [0, 1],
      duration: MIN_MS,
      ease: "inOutQuad",
    });
    return () => window.clearTimeout(timer);
  }, []);

  // Exit once data is ready and the minimum time has elapsed.
  useEffect(() => {
    if (!ready || !minDone || exiting.current) return;
    exiting.current = true;
    if (prefersReducedMotion() || !root.current) {
      onDone();
      return;
    }
    animate(root.current, {
      opacity: [1, 0],
      translateY: [0, -40],
      duration: 620,
      ease: "inOutQuad",
      onComplete: onDone,
    });
  }, [ready, minDone, onDone]);

  return (
    <div className="splash" ref={root} role="status" aria-live="polite">
      <span className="sr-only">Loading GridPulse…</span>
      <div className="splash-inner" aria-hidden="true">
        <svg className="splash-logo" viewBox="0 0 24 24">
          <defs>
            <linearGradient id="splashGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#4da3ff" />
              <stop offset="100%" stopColor="#36d6c6" />
            </linearGradient>
          </defs>
          <path d="M13 2 4 14h7l-1 8 9-12h-7l1-8Z" />
        </svg>
        <div className="splash-word">
          {WORD.split("").map((ch, i) => (
            <span key={`${ch}-${i}`} className="grad-text">
              {ch}
            </span>
          ))}
        </div>
        <p className="splash-tag">Accelerated peak-risk intelligence</p>
        <div className="splash-bar">
          <div className="splash-fill" />
        </div>
      </div>
    </div>
  );
}
