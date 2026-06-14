export interface SearchHistoryItem {
  id: string;
  query: string;
  provider_used: string | null;
  result_count: number | null;
  searched_at: string;
}

export interface SearchHistoryResponse {
  items: SearchHistoryItem[];
  total: number;
}

export interface Bookmark {
  id: string;
  document_id: string | null;
  folder_name: string;
  notes: string | null;
  created_at: string;
  title: string | null;
  court: string | null;
  date: string | null;
}

export interface BookmarksResponse {
  items: Bookmark[];
  folders: string[];
}

export interface BookmarkCreatePayload {
  document_id: string;
  folder_name?: string;
  notes?: string;
}

export interface BookmarkUpdatePayload {
  folder_name?: string;
  notes?: string;
}

export interface FeedbackPayload {
  query: string;
  is_helpful: boolean;
  provider_used?: string | null;
  search_id?: string;
}

export interface DailySearchCount {
  date: string;
  count: number;
}

export interface TopSearchTerm {
  term: string;
  count: number;
}

export interface ProviderCount {
  provider: string;
  count: number;
}

export interface FeedbackSummary {
  helpful: number;
  not_helpful: number;
  helpful_percent: number;
}

export interface NegativeFeedbackItem {
  query: string;
  provider_used: string | null;
  created_at: string;
}

export interface FailedQueryItem {
  query: string;
  failed_at: string;
}

export interface AdminStats {
  searches_today: number;
  searches_this_week: number;
  avg_response_time_ms: number | null;
  provider_distribution: ProviderCount[];
  searches_per_day: DailySearchCount[];
  top_search_terms: TopSearchTerm[];
  feedback_summary: FeedbackSummary;
  recent_negative_feedback: NegativeFeedbackItem[];
  recent_failed_queries: FailedQueryItem[];
}
