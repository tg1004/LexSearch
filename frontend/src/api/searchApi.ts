import type {
  ProvidersResponse,
  SearchRequest,
  SearchResponse,
} from '../types/search.types';
import { MAX_YEAR, MIN_YEAR } from '../types/search.types';
import { apiRequest } from './client';

function buildFiltersPayload(filters?: SearchRequest['filters']) {
  if (!filters) {
    return {
      court: [],
      case_type: [],
      outcome: [],
    };
  }

  let yearFrom =
    filters.year_from !== undefined && filters.year_from > MIN_YEAR
      ? filters.year_from
      : undefined;
  let yearTo =
    filters.year_to !== undefined && filters.year_to < MAX_YEAR
      ? filters.year_to
      : undefined;

  if (yearFrom !== undefined && yearTo !== undefined && yearFrom > yearTo) {
    [yearFrom, yearTo] = [yearTo, yearFrom];
  }

  return {
    court: filters.court ?? [],
    case_type: filters.case_type ?? [],
    outcome: filters.outcome ?? [],
    ...(yearFrom !== undefined ? { year_from: yearFrom } : {}),
    ...(yearTo !== undefined ? { year_to: yearTo } : {}),
  };
}

export function searchJudgements(payload: SearchRequest): Promise<SearchResponse> {
  return apiRequest<SearchResponse>(
    '/api/search',
    {
      method: 'POST',
      body: JSON.stringify({
        query: payload.query,
        preferred_provider: payload.preferred_provider ?? 'auto',
        filters: buildFiltersPayload(payload.filters),
        page: payload.page ?? 1,
      }),
    },
    false,
    120_000,
  );
}

export function getProviders(): Promise<ProvidersResponse> {
  return apiRequest<ProvidersResponse>('/api/providers');
}
