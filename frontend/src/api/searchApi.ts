import type {
  ProvidersResponse,
  SearchRequest,
  SearchResponse,
} from '../types/search.types';
import { apiRequest } from './client';

export function searchJudgements(payload: SearchRequest): Promise<SearchResponse> {
  return apiRequest<SearchResponse>('/api/search', {
    method: 'POST',
    body: JSON.stringify({
      query: payload.query,
      preferred_provider: payload.preferred_provider ?? 'auto',
      filters: {
        court: payload.filters?.court ?? [],
        year_from: payload.filters?.year_from,
        year_to: payload.filters?.year_to,
        case_type: payload.filters?.case_type ?? [],
        outcome: payload.filters?.outcome ?? [],
      },
      page: payload.page ?? 1,
    }),
  });
}

export function getProviders(): Promise<ProvidersResponse> {
  return apiRequest<ProvidersResponse>('/api/providers');
}
