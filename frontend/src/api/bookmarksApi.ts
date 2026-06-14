import { apiRequest } from './client';
import type {
  Bookmark,
  BookmarkCreatePayload,
  BookmarksResponse,
  BookmarkUpdatePayload,
} from '../types/dashboard.types';

export function getBookmarks(): Promise<BookmarksResponse> {
  return apiRequest<BookmarksResponse>('/api/bookmarks', {}, true);
}

export function createBookmark(payload: BookmarkCreatePayload): Promise<Bookmark> {
  return apiRequest<Bookmark>(
    '/api/bookmarks',
    { method: 'POST', body: JSON.stringify(payload) },
    true,
  );
}

export function updateBookmark(id: string, payload: BookmarkUpdatePayload): Promise<Bookmark> {
  return apiRequest<Bookmark>(
    `/api/bookmarks/${id}`,
    { method: 'PATCH', body: JSON.stringify(payload) },
    true,
  );
}

export function deleteBookmark(id: string): Promise<void> {
  return apiRequest<void>(`/api/bookmarks/${id}`, { method: 'DELETE' }, true);
}
