/**
 * Shared frontend types.
 *
 * Types here mirror the backend Pydantic schemas so the two stay in sync.
 * Some correspond to backend endpoints that are not implemented yet
 * (see backend/app/api/routes/*.py docstrings for status) — they're
 * defined now so components can be built against a stable shape.
 */

export interface HealthStatus {
  status: "ok" | "degraded";
  service: string;
  environment: string;
  database: "connected" | "unreachable";
}

// --- Auth (backend: implemented as of Day 2) ---
export interface User {
  id: string;
  email: string;
  full_name?: string | null;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload extends LoginPayload {
  full_name?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

// --- Documents (backend: implemented as of Day 2; extraction/chunking
// still Day 3, so "processing"/"ready"/"failed" aren't produced yet) ---
export type DocumentStatus = "uploaded" | "processing" | "ready" | "failed";

export interface OrgDocument {
  id: string;
  filename: string;
  original_filename: string;
  content_type: string;
  size_bytes: number;
  status: DocumentStatus;
  uploaded_at: string;
  owner_id: string;
}

// --- Search (backend: implemented as of Day 4) ---
export interface SearchResultItem {
  chunk_id: string;
  document_id: string;
  document_name: string;
  content: string;
  score: number;
}

export interface SearchResponse {
  query: string;
  results: SearchResultItem[];
}

// --- Chat / RAG (backend: implemented as of Day 5) ---
export interface SourceCitation {
  document_id: string;
  document_name: string;
  snippet: string;
  page?: number;
  /** Cosine similarity, 0 to 1, higher is more relevant. Optional since
   * not every citation source populates it. */
  score?: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: SourceCitation[];
  created_at: string;
}

export interface ChatCitationResult {
  chunk_id: string;
  document_id: string;
  document_name: string;
  snippet: string;
  score: number;
}

export interface ChatAnswer {
  answer: string;
  citations: ChatCitationResult[];
}

// --- Meetings (backend: implemented as of Day 6) ---
export type MeetingStatus = "pending" | "summarized" | "failed";

export interface Meeting {
  id: string;
  title: string;
  raw_notes: string;
  summary: string | null;
  meeting_date: string | null;
  status: MeetingStatus;
  created_at: string;
  owner_id: string;
}

export interface CreateMeetingPayload {
  title: string;
  raw_notes: string;
  meeting_date?: string;
}

// --- Decisions (backend: implemented as of Day 6) ---
export interface Decision {
  id: string;
  summary: string;
  context: string | null;
  source_type: "meeting" | "document";
  source_id: string;
  source_title: string;
  created_at: string;
}
