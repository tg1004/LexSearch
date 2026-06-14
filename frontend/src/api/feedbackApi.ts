import { apiRequest } from './client';
import type { FeedbackPayload } from '../types/dashboard.types';

export function submitFeedback(payload: FeedbackPayload): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/api/feedback', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
