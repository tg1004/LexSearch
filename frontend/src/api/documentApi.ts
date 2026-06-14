import type {
  DocumentDetail,
  DocumentSummaryResult,
  HighlightResult,
} from '../types/document.types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    if (typeof detail === 'string') {
      throw new Error(detail);
    }
    if (Array.isArray(detail)) {
      throw new Error(detail.map((item: { msg: string }) => item.msg).join(', '));
    }
    throw new Error(data.message || 'Request failed');
  }

  return data as T;
}

export function getDocument(documentId: string): Promise<DocumentDetail> {
  return request<DocumentDetail>(`/api/documents/${encodeURIComponent(documentId)}`);
}

export function generateDocumentSummary(documentId: string): Promise<DocumentSummaryResult> {
  return request<DocumentSummaryResult>(
    `/api/documents/${encodeURIComponent(documentId)}/summary`,
    { method: 'POST' },
  );
}

export function getDocumentHighlight(
  documentId: string,
  chunkIndex: number,
): Promise<HighlightResult> {
  const params = new URLSearchParams({ chunk_index: String(chunkIndex) });
  return request<HighlightResult>(
    `/api/documents/${encodeURIComponent(documentId)}/highlight?${params}`,
  );
}
