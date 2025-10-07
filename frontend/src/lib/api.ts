export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export type ApiError = { message: string };

export async function apiPost<T>(path: string, body: any, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(init?.headers || {}) },
    body: JSON.stringify(body),
    credentials: "include",
    ...init,
  });

  if (!res.ok) {
    const err = await safeJson(res);
    throw new Error(err?.detail || err?.message || "Request failed");
  }
  return (await res.json()) as T;
}

export async function apiPostForm<T>(path: string, form: URLSearchParams, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded", ...(init?.headers || {}) },
    body: form.toString(),
    credentials: "include",
    ...init,
  });

  if (!res.ok) {
    const err = await safeJson(res);
    throw new Error(err?.detail || err?.message || "Request failed");
  }
  return (await res.json()) as T;
}

async function safeJson(res: Response): Promise<any | null> {
  try {
    return await res.json();
  } catch {
    return null;
  }
}





