import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface TeamState {
  selectedTeamId: string | undefined;
  setSelectedTeamId: (teamId: string | undefined) => void;
}

/**
 * Store for managing the currently selected team.
 * Persists the selection in localStorage so it survives page reloads.
 */
export const useTeamStore = create<TeamState>()(
  persist(
    (set) => {
      return {
        selectedTeamId: undefined,
        setSelectedTeamId: (teamId) => {
          return set({ selectedTeamId: teamId });
        },
      };
    },
    {
      name: 'team-storage',
    }
  )
);

