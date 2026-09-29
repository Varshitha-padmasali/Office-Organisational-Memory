/**
 * Thin API client for talking to the FastAPI backend.
 *
 * `getHealth()` is the one fully functional call today — it hits the real
 * GET /health endpoint and is used by the dashboard to prove frontend <->
 * backend connectivity end-to-end on Day 1.
 *
 * Everything else (login, documents, chat) has a typed function stub that
 * throws a clear "not implemented" error, matching the backend's honest
 * HTTP 501 responses. These are here so components (login form, chat
 * input, upload widget) have a real function to call and swap in once the
 * backend implements each feature — see each function's `@status` note.
 */

import type { HealthStatus, LoginPayload, OrgDocument, User } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { "Content-Type": "application/json", ...(init?.headers ?? {}) },
      ...init,
    });
  } catch {
    throw new ApiError(
      `Could not reach the backend at ${API_BASE_URL}. Is it running?`
    );
  }

  if (!response.ok) {
    let message = `Request to ${path} failed with status ${response.status}`;
    try {
      const body = await response.json();
      message = body?.error?.message ?? message;
    } catch {
      // response wasn't JSON — keep the generic message
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

/** @status implemented — calls the real GET /health endpoint. */
export async function getHealth(): Promise<HealthStatus> {
  return request<HealthStatus>("/health");
}

/** @status NOT implemented on the backend yet (planned Day 2). Will 501. */
export async function login(payload: LoginPayload): Promise<User> {
  return request<User>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** @status NOT implemented on the backend yet (planned Day 2-3). Will 501. */
export async function listDocuments(): Promise<OrgDocument[]> {
  return request<OrgDocument[]>("/api/v1/documents/");
}

export { ApiError };
