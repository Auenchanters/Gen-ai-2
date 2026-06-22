import { animate, stagger } from "animejs";
import { type RefObject, useEffect, useLayoutEffect, useRef, useState } from "react";

/** True when the user has requested reduced motion (or no matchMedia, e.g. in tests). */
export function prefersReducedMotion(): boolean {
  return (
    typeof window === "undefined" ||
    typeof window.matchMedia !== "function" ||
    window.matchMedia("(prefers-reduced-motion: reduce)").matches
  );
}

/** Stagger-reveal matching descendants on mount (no-op under reduced motion). */
export function useReveal<T extends HTMLElement>(selector = ".reveal"): RefObject<T> {
  const ref = useRef<T>(null);
  useLayoutEffect(() => {
    const root = ref.current;
    if (!root || prefersReducedMotion()) {
      return;
    }
    const targets = Array.from(root.querySelectorAll<HTMLElement>(selector));
    if (targets.length === 0) {
      return;
    }
    for (const element of targets) {
      element.style.opacity = "0";
      element.style.transform = "translateY(18px)";
    }
    animate(targets, {
      opacity: 1,
      translateY: 0,
      delay: stagger(70),
      duration: 560,
      ease: "outQuad",
    });
  }, [selector]);
  return ref;
}

/** Animate a number from 0 to `value` on mount; returns the value immediately if reduced. */
export function useCountUp(value: number): number {
  const [display, setDisplay] = useState(() => (prefersReducedMotion() ? value : 0));
  useEffect(() => {
    if (prefersReducedMotion()) {
      setDisplay(value);
      return;
    }
    const state = { v: 0 };
    const animation = animate(state, {
      v: value,
      duration: 850,
      ease: "outExpo",
      onUpdate: () => setDisplay(state.v),
    });
    return () => {
      animation.pause();
    };
  }, [value]);
  return display;
}
