import { apiRequest } from './client';
import type { AdminStats } from '../types/dashboard.types';

export function getAdminStats(): Promise<AdminStats> {
  return apiRequest<AdminStats>('/api/admin/stats', {}, true);
}
