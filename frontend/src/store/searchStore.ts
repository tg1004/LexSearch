import { create } from 'zustand';
import type { SearchFilters } from '../types/search.types';
import { MAX_YEAR, MIN_YEAR } from '../types/search.types';

export const EMPTY_FILTERS: SearchFilters = {
  court: [],
  year_from: MIN_YEAR,
  year_to: MAX_YEAR,
  case_type: [],
  outcome: [],
};

interface SearchState {
  lastQuery: string;
  filters: SearchFilters;
  setLastQuery: (query: string) => void;
  setFilters: (filters: SearchFilters) => void;
  resetFilters: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  lastQuery: '',
  filters: { ...EMPTY_FILTERS },
  setLastQuery: (query) => set({ lastQuery: query }),
  setFilters: (filters) => set({ filters }),
  resetFilters: () => set({ filters: { ...EMPTY_FILTERS } }),
}));
