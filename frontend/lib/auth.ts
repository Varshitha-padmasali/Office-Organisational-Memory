/**
 * Auth helpers.
 *
 * STATUS: NOT IMPLEMENTED YET — planned for Day 2, once the backend's
 * /api/v1/auth/login is real. There is intentionally no token storage,
 * no session persistence, and no route protection yet: the login page is
 * a static UI placeholder (see app/login/page.tsx) so we don't ship a
 * fake "logged in" experience.
 */

export function isAuthenticated(): boolean {
    // TODO (Day 2): check for a stored/valid JWT.
    return false;
  }
  