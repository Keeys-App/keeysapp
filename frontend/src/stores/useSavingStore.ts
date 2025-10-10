import { create } from 'zustand';

interface SavingStore {
  isSaving: boolean;
  savingMessage: string;
  startSaving: (message?: string) => void;
  stopSaving: () => void;
}

export const useSavingStore = create<SavingStore>((set) => ({
  isSaving: false,
  savingMessage: 'Saving...',
  startSaving: (message = 'Saving...') => set({ isSaving: true, savingMessage: message }),
  stopSaving: () => set({ isSaving: false }),
}));

/**
 * Hook for managing saving state
 * Returns a function that can be used to wrap async operations
 */
export const useSaving = () => {
  const { startSaving, stopSaving } = useSavingStore();

  return async <T,>(
    asyncFn: () => Promise<T>,
    message?: string
  ): Promise<T> => {
    startSaving(message);
    try {
      const result = await asyncFn();
      return result;
    } finally {
      stopSaving();
    }
  };
};

