export interface SearchFilters {
  court: string[];
  year_from?: number;
  year_to?: number;
  case_type: string[];
  outcome: string[];
}

export interface SearchRequest {
  query: string;
  preferred_provider?: string;
  filters?: SearchFilters;
  page?: number;
}

export interface Citation {
  number: number;
  document_id: string;
  passage: string;
  title: string;
  court: string | null;
  date: string | null;
}

export interface Source {
  document_id: string;
  title: string;
  court: string | null;
  date: string | null;
  snippet: string;
  score: number;
  chunk_index: number | null;
}

export interface SearchResponse {
  answer: string;
  citations: Citation[];
  sources: Source[];
  provider_used: string | null;
  related_questions: string[];
  search_id: string;
  result_count: number;
}

export interface ProviderInfo {
  name: string;
  label: string;
  model: string | null;
  available: boolean;
}

export interface ProvidersResponse {
  providers: ProviderInfo[];
}

export type PreferredProvider = 'auto' | 'groq' | 'gemini';

export const COURT_OPTIONS = [
  'Supreme Court',
  'Delhi High Court',
  'Bombay High Court',
  'Madras High Court',
  'Calcutta High Court',
  'Karnataka High Court',
  'Allahabad High Court',
  'Gujarat High Court',
  'Punjab and Haryana High Court',
  'Rajasthan High Court',
] as const;

export const CASE_TYPE_OPTIONS = [
  'Constitutional',
  'Criminal',
  'Civil',
  'Family',
  'Tax',
  'Labour',
  'Property',
] as const;

export const OUTCOME_OPTIONS = [
  'Allowed',
  'Dismissed',
  'Partly Allowed',
  'Set Aside',
  'Remanded',
  'Upheld',
] as const;

export const MIN_YEAR = 1950;
export const MAX_YEAR = new Date().getFullYear();
