import { create } from 'zustand';

interface LayoutState {
  // Key Management Panel
  isPanelOpen: boolean;
  showPanelToggle: boolean;
  togglePanel: () => void;
  setShowPanelToggle: (show: boolean) => void;
}

export const useLayoutStore = create<LayoutState>((set) => {
  // Load initial panel state from localStorage
  const saved = localStorage.getItem('keyManagementPanelOpen');
  const initialPanelOpen = saved !== null ? saved === 'true' : true;

  return {
    isPanelOpen: initialPanelOpen,
    showPanelToggle: false,
    togglePanel: () => {
      return set((state) => {
        const newState = !state.isPanelOpen;
        localStorage.setItem('keyManagementPanelOpen', String(newState));
        return { isPanelOpen: newState };
      });
    },
    setShowPanelToggle: (show: boolean) => {
      return set({ showPanelToggle: show });
    },
  };
});

