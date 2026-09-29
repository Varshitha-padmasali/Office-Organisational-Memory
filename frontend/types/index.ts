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
  
  // --- Auth (backend: not implemented yet, planned Day 2) ---
  export interface User {
    id: string;
    email: string;
    full_name?: string | null;
  }
  
  export interface LoginPayload {
    email: string;
    password: string;
  }
  
  // --- Documents (backend: not implemented yet, planned Day 2-3) ---
  export type DocumentStatus = "uploading" | "processing" | "ready" | "failed";
  
  export interface OrgDocument {
    id: string;
    filename: string;
    status: DocumentStatus;
    uploaded_at: string;
    size_bytes: number;
  }
  
  // --- Chat / RAG (backend: not implemented yet, planned Day 4-5) ---
  export interface SourceCitation {
    document_id: string;
    document_name: string;
    snippet: string;
    page?: number;
  }
  
  export interface ChatMessage {
    id: string;
    role: "user" | "assistant";
    content: string;
    citations?: SourceCitation[];
    created_at: string;
  }
  