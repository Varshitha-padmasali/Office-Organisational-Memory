"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login, register, ApiError } from "@/lib/api";
import { setToken } from "@/lib/auth";

/**
 * Login / register page.
 *
 * STATUS (Day 2): fully functional against the real backend. A single
 * form toggles between "Sign in" and "Create account" — both hit real
 * endpoints and store the returned JWT (see lib/token.ts), then redirect
 * to the dashboard.
 */
export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      const response =
        mode === "login"
          ? await login({ email, password })
          : await register({ email, password, full_name: fullName || undefined });

      setToken(response.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-gray-50 -m-4 md:-m-8">
      <div className="w-full max-w-sm bg-white rounded-xl shadow-sm border border-gray-200 p-8">
        <h1 className="text-xl font-semibold text-gray-900 mb-1">
          {mode === "login" ? "Sign in" : "Create account"}
        </h1>
        <p className="text-sm text-gray-500 mb-6">
          Access your organization&apos;s knowledge base.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === "register" && (
            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-1">
                Full name
              </label>
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Doe"
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
              />
            </div>
          )}

          <div>
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@company.com"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-brand-500 px-3 py-2 text-sm font-medium text-white hover:bg-brand-600 transition-colors disabled:opacity-50"
          >
            {submitting ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
          </button>
        </form>

        {error && (
          <div className="mt-4 rounded-md bg-red-50 border border-red-200 px-3 py-2 text-xs text-red-700">
            {error}
          </div>
        )}

        <button
          type="button"
          onClick={() => {
            setMode(mode === "login" ? "register" : "login");
            setError(null);
          }}
          className="mt-4 w-full text-center text-xs text-brand-600 hover:underline"
        >
          {mode === "login"
            ? "Need an account? Create one"
            : "Already have an account? Sign in"}
        </button>
      </div>
    </div>
  );
}
