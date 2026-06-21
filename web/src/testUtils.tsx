import axe from "axe-core";

/** Run axe against a rendered container and return violations.
 *
 * `region` is disabled because isolated components render outside the page's landmark
 * structure in unit tests; `color-contrast` is disabled because jsdom has no real layout
 * or canvas to measure it (contrast is enforced in the stylesheet instead).
 */
export async function a11yViolations(container: HTMLElement) {
  const results = await axe.run(container, {
    rules: { region: { enabled: false }, "color-contrast": { enabled: false } },
  });
  return results.violations;
}
