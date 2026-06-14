import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as bookmarksApi from '../api/bookmarksApi';
import type { BookmarkCreatePayload, BookmarkUpdatePayload } from '../types/dashboard.types';

export function useBookmarks(enabled = true) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['bookmarks'],
    queryFn: bookmarksApi.getBookmarks,
    enabled,
  });

  const invalidate = () => queryClient.invalidateQueries({ queryKey: ['bookmarks'] });

  const addBookmark = useMutation({
    mutationFn: (payload: BookmarkCreatePayload) => bookmarksApi.createBookmark(payload),
    onSuccess: invalidate,
  });

  const editBookmark = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: BookmarkUpdatePayload }) =>
      bookmarksApi.updateBookmark(id, payload),
    onSuccess: invalidate,
  });

  const removeBookmark = useMutation({
    mutationFn: bookmarksApi.deleteBookmark,
    onSuccess: invalidate,
  });

  return {
    items: query.data?.items ?? [],
    folders: query.data?.folders ?? ['General'],
    isLoading: query.isLoading,
    error: query.error,
    addBookmark: addBookmark.mutateAsync,
    editBookmark: editBookmark.mutateAsync,
    removeBookmark: removeBookmark.mutateAsync,
    isSaving: addBookmark.isPending || editBookmark.isPending,
    refetch: query.refetch,
  };
}
