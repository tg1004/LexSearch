import { useAuthStore } from '../store/authStore';

function normalizeApiUrl(url: string): string {
  const trimmed = url.trim().replace(/\/+$/, '');
  if (!trimmed) return '';
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return trimmed;
  }
  // Vercel env vars sometimes omit the scheme — fetch() treats that as a relative path!
  return `https://${trimmed}`;
}

// In dev, use relative URLs so Vite proxies /api → backend (see vite.config.ts).
// In production, VITE_API_URL must be set at build time (e.g. Railway backend URL).
const API_URL = import.meta.env.DEV
  ? ''
  : normalizeApiUrl(import.meta.env.VITE_API_URL || 'http://localhost:8000');

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  requireAuth = false,
  timeoutMs = 30_000,
): Promise<T> {
  const token = useAuthStore.getState().token;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  } else if (requireAuth) {
    throw new Error('Please log in to continue');
  }

  let response: Response;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof Error && err.name === 'AbortError') {
      throw new Error('Request timed out. Try again or narrow your filters.');
    }
    const hint = import.meta.env.DEV
      ? ' Is the backend running? Start it with: cd backend && uvicorn app.main:app --reload --port 8000'
      : ` Check VITE_API_URL (${import.meta.env.VITE_API_URL || 'not set'}) and backend CORS.`;
    throw new Error(`Failed to fetch${hint}`);
  } finally {
    clearTimeout(timeoutId);
  }

  if (response.status === 429) {
    throw new Error('Too many requests. Please wait a moment and try again.');
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    if (typeof detail === 'string') {
      throw new Error(detail);
    }
    if (Array.isArray(detail)) {
      throw new Error(detail.map((item: { msg: string }) => item.msg).join(', '));
    }
    throw new Error(data.message || 'Request failed');
  }

  return data as T;
}
