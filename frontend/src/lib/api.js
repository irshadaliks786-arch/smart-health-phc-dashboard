// Fixed at build/runtime via env — never guessed, never random.
const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8080";

async function get(path) {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`GET ${path} failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export const api = {
  districts: () => get("/api/districts"),
  phcs: (params = {}) => {
    const qs = new URLSearchParams(params).toString();
    return get(`/api/phcs${qs ? `?${qs}` : ""}`);
  },
  redistribution: (priority) =>
    get(`/api/redistribution${priority ? `?priority=${priority}` : ""}`),
  insights: () => get("/api/insights"),
  health: () => get("/health"),
};
