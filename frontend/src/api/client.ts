import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  requireAuth = false,
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

  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
  });

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
