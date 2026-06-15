import { apiRequest } from './client';
import type { AuthResponse, LoginPayload, SignupPayload, User } from '../types/auth.types';

export function signup(payload: SignupPayload): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function login(payload: LoginPayload): Promise<AuthResponse> {
  return apiRequest<AuthResponse>('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getMe(token: string): Promise<User> {
  return apiRequest<User>('/api/auth/me', {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function logout(): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/api/auth/logout', { method: 'POST' });
}
