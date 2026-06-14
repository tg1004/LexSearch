import { useQuery } from '@tanstack/react-query';
import { searchJudgements } from '../api/searchApi';
import type { SearchFilters } from '../types/search.types';
import { MAX_YEAR, MIN_YEAR } from '../types/search.types';

export interface UseSearchParams {
  query: string;
  preferredProvider?: string;
  filters?: SearchFilters;
  page?: number;
  enabled?: boolean;
}

function buildApiFilters(filters?: SearchFilters): SearchFilters | undefined {
  if (!filters) return undefined;

  const yearFrom =
    filters.year_from !== undefined && filters.year_from > MIN_YEAR
      ? filters.year_from
      : undefined;
  const yearTo =
    filters.year_to !== undefined && filters.year_to < MAX_YEAR ? filters.year_to : undefined;

  return {
    court: filters.court,
    case_type: filters.case_type,
    outcome: filters.outcome,
    year_from: yearFrom,
    year_to: yearTo,
  };
}

export function useSearch({
  query,
  preferredProvider = 'auto',
  filters,
  page = 1,
  enabled = true,
}: UseSearchParams) {
  const trimmedQuery = query.trim();

  return useQuery({
    queryKey: ['search', trimmedQuery, preferredProvider, filters, page],
    queryFn: () =>
      searchJudgements({
        query: trimmedQuery,
        preferred_provider: preferredProvider,
        filters: buildApiFilters(filters),
        page,
      }),
    enabled: enabled && trimmedQuery.length > 0,
    retry: 1,
    staleTime: 5 * 60 * 1000,
  });
}
