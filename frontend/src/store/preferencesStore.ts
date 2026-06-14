import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { PreferredProvider } from '../types/search.types';

interface PreferencesState {
  preferredProvider: PreferredProvider;
  setPreferredProvider: (provider: PreferredProvider) => void;
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      preferredProvider: 'auto',
      setPreferredProvider: (provider) => set({ preferredProvider: provider }),
    }),
    { name: 'lexsearch-preferences' },
  ),
);
