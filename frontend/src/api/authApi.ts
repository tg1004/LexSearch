import type { AuthResponse, LoginPayload, SignupPayload, User } from '../types/auth.types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

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

export function signup(payload: SignupPayload): Promise<AuthResponse> {
  return request<AuthResponse>('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function login(payload: LoginPayload): Promise<AuthResponse> {
  return request<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getMe(token: string): Promise<User> {
  return request<User>('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function logout(): Promise<{ message: string }> {
  return request<{ message: string }>('/api/auth/logout', { method: 'POST' });
}
