/**
 * Thin API client for talking to the FastAPI backend.
 *
 * STATUS (Day 2): getHealth(), login(), register(), getCurrentUser(),
 * listDocuments(), and uploadDocument() are all fully functional against
 * the real backend. Chat/meetings/decisions/knowledge-gaps endpoints
 * still 501 on the backend (planned Day 4-7) — no client functions exist
 * for them yet, to avoid calling something that can't work.
 */

import { clearToken, getToken } from "@/lib/token";
import type {
  ChatAnswer,
  HealthStatus,
  LoginPayload,
  OrgDocument,
  RegisterPayload,
  SearchResponse,
  TokenResponse,
  User,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

class ApiError extends Error {
  status?: number;
  constructor(message: string, status?: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function parseErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const body = await response.json();
    return body?.error?.message ?? fallback;
  } catch {
    return fallback;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...(init?.headers ?? {}),
      },
      ...init,
    });
  } catch {
    throw new ApiError(`Could not reach the backend at ${API_BASE_URL}. Is it running?`);
  }

  if (!response.ok) {
    const message = await parseErrorMessage(
      response,
      `Request to ${path} failed with status ${response.status}`
    );
    if (response.status === 401) {
      // Stored token is missing/expired/invalid — drop it so the UI
      // correctly falls back to "signed out" instead of retrying forever.
      clearToken();
    }
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<T>;
}

/** @status implemented — calls the real GET /health endpoint. */
export async function getHealth(): Promise<HealthStatus> {
  return request<HealthStatus>("/health");
}

/** @status implemented (Day 2) — real login against the backend. */
export async function login(payload: LoginPayload): Promise<TokenResponse> {
  return request<TokenResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** @status implemented (Day 2) — real registration; also returns a token (auto-login). */
export async function register(payload: RegisterPayload): Promise<TokenResponse> {
  return request<TokenResponse>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

/** @status implemented (Day 2) — resolves the currently-stored token to a user. */
export async function getCurrentUser(): Promise<User> {
  return request<User>("/api/v1/auth/me");
}

/** @status implemented (Day 2) — lists the signed-in user's own documents. */
export async function listDocuments(): Promise<OrgDocument[]> {
  return request<OrgDocument[]>("/api/v1/documents/");
}

/**
 * @status implemented (Day 4) — real semantic search over the signed-in
 * user's own "ready" documents. Returns ranked raw passages, not a
 * generated answer (that's Day 5) — see ChatWindow.tsx for how this is
 * presented in the meantime.
 */
export async function searchDocuments(query: string, topK = 5): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query, top_k: String(topK) });
  return request<SearchResponse>(`/api/v1/search/?${params.toString()}`);
}

/**
 * @status implemented (Day 5) - generates a real answer from the
 * signed-in user's own "ready" documents, grounded on the chunks
 * retrieved by the same search used in searchDocuments(). Returns the
 * generated text plus the citations it was grounded on.
 */
export async function sendChatMessage(question: string, topK = 5): Promise<ChatAnswer> {
  return request<ChatAnswer>("/api/v1/chat/", {
    method: "POST",
    body: JSON.stringify({ question, top_k: topK }),
  });
}

/**
 * @status implemented (Day 2). Bypasses `request()` because file uploads
 * use multipart/form-data — the browser must set that Content-Type
 * (including the boundary) itself, so we must NOT set it manually.
 */
export async function uploadDocument(file: File): Promise<OrgDocument> {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/documents/upload`, {
      method: "POST",
      headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      body: formData,
    });
  } catch {
    throw new ApiError(`Could not reach the backend at ${API_BASE_URL}. Is it running?`);
  }

  if (!response.ok) {
    const message = await parseErrorMessage(response, `Upload failed with status ${response.status}`);
    throw new ApiError(message, response.status);
  }

  return response.json() as Promise<OrgDocument>;
}

export { ApiError };
