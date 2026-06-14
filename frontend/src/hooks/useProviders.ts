import { useQuery } from '@tanstack/react-query';
import { getProviders } from '../api/searchApi';

export function useProviders() {
  return useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
    staleTime: 5 * 60 * 1000,
  });
}
