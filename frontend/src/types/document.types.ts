export interface DocumentDetail {
  id: string;
  title: string;
  court: string | null;
  date: string | null;
  judges: string[];
  case_type: string | null;
  outcome: string | null;
  bench_size: string | null;
  full_text: string;
  summary: string | null;
  url: string | null;
}

export interface DocumentSummaryResult {
  document_id: string;
  summary: string;
  provider_used: string | null;
}

export interface HighlightResult {
  document_id: string;
  chunk_index: number;
  highlighted_passage: string;
  position: number;
  char_end: number;
}
