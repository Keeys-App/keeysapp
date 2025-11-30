# Onboarding Components

This directory contains components for the user onboarding wizard flow.

## Overview

The onboarding wizard guides new users through the initial setup:
1. **Create Team** - Create their first team workspace
2. **Invite Members** - Optionally invite team members (can be skipped)
3. **Create Project** - Create their first localization project

## Components

### `OnboardingWizard.tsx`

Main wizard component that orchestrates the three-step flow:
- Manages step navigation
- Shows progress indicator
- Handles wizard state via `useOnboardingStore`

**Usage:**
```tsx
<OnboardingWizard />
```

### `CreateTeamStep.tsx`

First step - team creation form.

**Props:**
- `onNext: (teamId: string) => void` - Called when team is created successfully

**Features:**
- Team name (required)
- Team description (optional)
- Uses `CREATE_TEAM` mutation
- Automatically sets created team as selected in `useTeamStore`

### `InviteMembersStep.tsx`

Second step - invite team members (optional).

**Props:**
- `teamId: string` - The team to invite members to
- `onNext: () => void` - Called when continuing with invites
- `onSkip: () => void` - Called when skipping this step

**Features:**
- Add multiple members by email
- Select role for each member
- Remove invited members before submitting
- Can skip this step entirely
- Uses `ADD_TEAM_MEMBER` mutation

### `CreateProjectStep.tsx`

Third and final step - create first project.

**Props:**
- `teamId: string` - The team to create project in
- `onComplete: () => void` - Called when project is created

**Features:**
- Project name (required)
- Project description (optional)
- Color picker
- Language configuration (pre-populated with English as default)
- Default language selection (English pre-selected)
- Uses `CREATE_PROJECT` mutation
- Redirects to created project on success

## Store

### `useOnboardingStore` (`stores/onboardingStore.ts`)

Manages onboarding state using Zustand with persistence:

**State:**
- `isOnboardingComplete: boolean` - Whether user completed onboarding
- `currentStep: number` - Current wizard step (1-3)
- `createdTeamId: string | null` - ID of created team
- `invitedMembers: string[]` - List of invited member emails
- `createdProjectId: string | null` - ID of created project

**Actions:**
- `setOnboardingComplete(complete: boolean)` - Mark onboarding as complete
- `setCurrentStep(step: number)` - Update current step
- `setCreatedTeamId(teamId: string | null)` - Save created team ID
- `addInvitedMember(email: string)` - Add invited member email
- `setCreatedProjectId(projectId: string | null)` - Save created project ID
- `resetOnboarding()` - Reset all onboarding state

**Persistence:**
State is persisted to localStorage as `onboarding-storage`.

## Flow

### Registration Flow

1. User registers on `/auth`
2. `AuthPage` checks if user has any teams (via `GET_TEAMS` query)
3. If no teams → redirect to `/onboarding`
4. If has teams → redirect to `/dashboard`

### Onboarding Flow

1. **Step 1: Create Team**
   - User enters team name and description
   - Clicks "Continue"
   - Team created via `CREATE_TEAM` mutation
   - Team ID saved to onboarding store
   - Team automatically set as selected in `useTeamStore`
   - Advances to Step 2

2. **Step 2: Invite Members (Optional)**
   - User can add multiple members by email + role
   - Each invite uses `ADD_TEAM_MEMBER` mutation
   - User can:
     - Click "Continue" to proceed (if members added)
     - Click "Skip for now" to skip
   - Advances to Step 3

3. **Step 3: Create Project**
   - Form pre-populated with English language as default
   - User enters project name and optionally adds more languages
   - Clicks "Create Project & Finish"
   - Project created via `CREATE_PROJECT` mutation
   - Onboarding marked as complete
   - User redirected to created project page

## Routes

- `/onboarding` - Onboarding wizard page (protected route, no layout)
  - Cannot be bypassed - all other protected pages redirect here if onboarding incomplete
  - Uses ProtectedRoute but not Layout (fullscreen wizard)
  - Accessible only to authenticated users who haven't completed onboarding

## Protection

The onboarding system ensures users complete the setup:

**OnboardingPage protection:**
- Requires authentication (via `ProtectedRoute`)
- If `isOnboardingComplete` is true → redirects to dashboard
- If not authenticated → redirects to `/auth`

**Layout protection (all main pages):**
- If `isOnboardingComplete` is false → redirects to `/onboarding`
- Users cannot bypass onboarding by changing URL
- All routes under Layout component are protected

## UI/UX

### Progress Indicator

Visual step indicator at the top shows:
- Current step (primary color)
- Completed steps (green with checkmark)
- Upcoming steps (muted)
- Connected by progress lines

### Navigation

- No back button (forward-only flow)
- Step 2 can be skipped
- No "Cancel" button (must complete onboarding)
- Wizard fills full viewport (no header/footer)

### Styling

- Centered card layout
- Max width: 3xl
- Responsive design
- Uses shadcn/ui components
- Consistent spacing and typography

## Testing

Manual testing checklist:
- [ ] New user registration redirects to onboarding
- [ ] Step 1: Create team with valid data
- [ ] Step 1: Validation for empty team name
- [ ] Step 1: Created team becomes selected team
- [ ] Step 2: Add multiple members with different roles
- [ ] Step 2: Prevent duplicate emails
- [ ] Step 2: Skip to step 3
- [ ] Step 3: English language pre-populated
- [ ] Step 3: Create project with languages
- [ ] Step 3: Validation for required fields
- [ ] Complete wizard redirects to created project
- [ ] `isOnboardingComplete` set to true after completion
- [ ] Returning to `/onboarding` after completion redirects to dashboard
- [ ] **Trying to navigate to `/`, `/teams`, or any other route during onboarding redirects back to `/onboarding`**
- [ ] **Manually changing URL in browser during onboarding redirects to `/onboarding`**
- [ ] After completing onboarding, can freely navigate between pages

## Future Enhancements

Potential improvements:
- [ ] Add step validation before allowing next
- [ ] Show success animations between steps
- [ ] Add "Save & Exit" to resume later
- [ ] Email verification before onboarding
- [ ] Import existing projects option
- [ ] Team templates (e.g., "Development Team", "Marketing Team")
- [ ] Project templates with pre-configured languages

