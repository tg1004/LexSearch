import { apiRequest } from './client';
import type { SearchHistoryResponse } from '../types/dashboard.types';

export function getSearchHistory(): Promise<SearchHistoryResponse> {
  return apiRequest<SearchHistoryResponse>('/api/history', {}, true);
}

export function clearSearchHistory(): Promise<void> {
  return apiRequest<void>('/api/history', { method: 'DELETE' }, true);
}

export function deleteSearchHistoryEntry(id: string): Promise<void> {
  return apiRequest<void>(`/api/history/${id}`, { method: 'DELETE' }, true);
}
