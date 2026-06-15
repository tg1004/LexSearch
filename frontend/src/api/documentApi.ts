import { apiRequest } from './client';
import type {
  DocumentDetail,
  DocumentSummaryResult,
  HighlightResult,
} from '../types/document.types';

export function getDocument(documentId: string): Promise<DocumentDetail> {
  return apiRequest<DocumentDetail>(`/api/documents/${encodeURIComponent(documentId)}`);
}

export function generateDocumentSummary(documentId: string): Promise<DocumentSummaryResult> {
  return apiRequest<DocumentSummaryResult>(
    `/api/documents/${encodeURIComponent(documentId)}/summary`,
    { method: 'POST' },
  );
}

export function getDocumentHighlight(
  documentId: string,
  chunkIndex: number,
): Promise<HighlightResult> {
  const params = new URLSearchParams({ chunk_index: String(chunkIndex) });
  return apiRequest<HighlightResult>(
    `/api/documents/${encodeURIComponent(documentId)}/highlight?${params}`,
  );
}
