import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as historyApi from '../api/historyApi';

export function useSearchHistory(enabled = true) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ['history'],
    queryFn: historyApi.getSearchHistory,
    enabled,
  });

  const clearAll = useMutation({
    mutationFn: historyApi.clearSearchHistory,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['history'] }),
  });

  const removeEntry = useMutation({
    mutationFn: historyApi.deleteSearchHistoryEntry,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['history'] }),
  });

  return {
    items: query.data?.items ?? [],
    total: query.data?.total ?? 0,
    isLoading: query.isLoading,
    error: query.error,
    clearAll: clearAll.mutateAsync,
    removeEntry: removeEntry.mutateAsync,
    isClearing: clearAll.isPending,
  };
}
