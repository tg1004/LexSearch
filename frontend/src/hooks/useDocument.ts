import { useQuery } from '@tanstack/react-query';
import { getDocument, getDocumentHighlight, generateDocumentSummary } from '../api/documentApi';

export function useDocument(documentId: string) {
  return useQuery({
    queryKey: ['document', documentId],
    queryFn: () => getDocument(documentId),
    enabled: !!documentId,
    staleTime: 10 * 60 * 1000,
  });
}

export function useDocumentHighlight(documentId: string, chunkIndex: number | null) {
  return useQuery({
    queryKey: ['document-highlight', documentId, chunkIndex],
    queryFn: () => getDocumentHighlight(documentId, chunkIndex!),
    enabled: !!documentId && chunkIndex !== null && chunkIndex >= 0,
    staleTime: 30 * 60 * 1000,
  });
}

export function useDocumentSummary(documentId: string, enabled: boolean) {
  return useQuery({
    queryKey: ['document-summary', documentId],
    queryFn: () => generateDocumentSummary(documentId),
    enabled: enabled && !!documentId,
    staleTime: 60 * 60 * 1000,
    retry: 1,
  });
}
