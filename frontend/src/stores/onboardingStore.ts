import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface OnboardingState {
  isOnboardingComplete: boolean;
  currentStep: number;
  createdTeamId: string | null;
  invitedMembers: string[];
  createdProjectId: string | null;
  returnUrl: string | null;
  
  setOnboardingComplete: (complete: boolean) => void;
  setCurrentStep: (step: number) => void;
  setCreatedTeamId: (teamId: string | null) => void;
  addInvitedMember: (email: string) => void;
  setCreatedProjectId: (projectId: string | null) => void;
  setReturnUrl: (url: string | null) => void;
  resetOnboarding: () => void;
}

export const useOnboardingStore = create<OnboardingState>()(
  persist(
    (set) => ({
      isOnboardingComplete: false,
      currentStep: 1,
      createdTeamId: null,
      invitedMembers: [],
      createdProjectId: null,
      returnUrl: null,

      setOnboardingComplete: (complete) => {
        set({ isOnboardingComplete: complete });
      },

      setCurrentStep: (step) => {
        set({ currentStep: step });
      },

      setCreatedTeamId: (teamId) => {
        set({ createdTeamId: teamId });
      },

      addInvitedMember: (email) => {
        set((state) => ({
          invitedMembers: [...state.invitedMembers, email],
        }));
      },

      setCreatedProjectId: (projectId) => {
        set({ createdProjectId: projectId });
      },

      setReturnUrl: (url) => {
        set({ returnUrl: url });
      },

      resetOnboarding: () => {
        set({
          isOnboardingComplete: false,
          currentStep: 1,
          createdTeamId: null,
          invitedMembers: [],
          createdProjectId: null,
          returnUrl: null,
        });
      },
    }),
    {
      name: 'onboarding-storage',
    }
  )
);

