/**
 * Small, dependency-free utility helpers.
 */

/** Joins class names, skipping falsy values. A minimal stand-in for `clsx`. */
export function cn(...classes: Array<string | false | null | undefined>): string {
  return classes.filter(Boolean).join(" ");
}

/** Formats an ISO date string for display. Falls back gracefully if invalid. */
export function formatDate(iso: string): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return iso;
  return date.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}
