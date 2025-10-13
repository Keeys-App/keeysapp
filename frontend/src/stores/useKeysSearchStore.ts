import { create } from 'zustand';

interface KeysSearchState {
  search: string;
  setSearch: (search: string) => void;
  clearSearch: () => void;
}

export const useKeysSearchStore = create<KeysSearchState>((set) => ({
  search: '',
  setSearch: (search: string) => {
    return set({ search });
  },
  clearSearch: () => {
    return set({ search: '' });
  },
}));

