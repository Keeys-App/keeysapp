import { type FC } from 'react';
import { useMutation } from '@apollo/client';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useOnboardingStore, useTeamStore } from '@/stores';
import { CreateTeamStep } from './CreateTeamStep';
import { InviteMembersStep } from './InviteMembersStep';
import { CreateProjectStep } from './CreateProjectStep';
import { CheckCircle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { COMPLETE_ONBOARDING_MUTATION } from '@/graphql/auth';

export const OnboardingWizard: FC = () => {
  const {
    currentStep,
    createdTeamId,
    setCurrentStep,
    setCreatedTeamId,
    setOnboardingComplete,
  } = useOnboardingStore();

  const { setSelectedTeamId } = useTeamStore();
  const [completeOnboardingMutation] = useMutation(COMPLETE_ONBOARDING_MUTATION);

  const steps = [
    { number: 1, title: 'Create Team', description: 'Set up your team workspace' },
    { number: 2, title: 'Invite Members', description: 'Add team members (optional)' },
    { number: 3, title: 'Create Project', description: 'Start your first project' },
  ];

  const handleTeamCreated = (teamId: string) => {
    setCreatedTeamId(teamId);
    // Set the newly created team as selected in TeamStore
    setSelectedTeamId(teamId);
    setCurrentStep(2);
  };

  const handleMembersInvited = () => {
    setCurrentStep(3);
  };

  const handleProjectCreated = async () => {
    try {
      // Mark onboarding as complete in backend
      await completeOnboardingMutation();
      // Update local state
      setOnboardingComplete(true);
      // Navigation is handled in CreateProjectStep
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
      // Still mark as complete locally if backend fails
      setOnboardingComplete(true);
    }
  };

  return (
    <div className="flex h-full items-center justify-center p-6">
      <Card className="w-full max-w-3xl">
        <CardHeader>
          <CardTitle className="text-2xl">Welcome to Locales! 🎉</CardTitle>
          <CardDescription>
            Let's get you started with a few quick steps
          </CardDescription>

          {/* Progress Steps */}
          <div className="pt-6">
            <div className="flex items-center justify-between">
              {steps.map((step, index) => {
                return (
                  <div key={step.number} className="flex flex-1 items-center">
                    <div className="flex flex-col items-center">
                      <div
                        className={cn(
                          'flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors',
                          currentStep === step.number
                            ? 'border-primary bg-primary text-primary-foreground'
                            : currentStep > step.number
                              ? 'border-green-500 bg-green-500 text-white'
                              : 'border-muted bg-muted text-muted-foreground'
                        )}
                      >
                        {currentStep > step.number ? (
                          <CheckCircle className="h-5 w-5" />
                        ) : (
                          <span className="font-semibold">{step.number}</span>
                        )}
                      </div>
                      <div className="mt-2 text-center">
                        <p
                          className={cn(
                            'text-sm font-medium',
                            currentStep === step.number
                              ? 'text-foreground'
                              : 'text-muted-foreground'
                          )}
                        >
                          {step.title}
                        </p>
                        <p className="text-xs text-muted-foreground">
                          {step.description}
                        </p>
                      </div>
                    </div>
                    {index < steps.length - 1 ? (
                      <div
                        className={cn(
                          'mx-4 h-0.5 flex-1 transition-colors',
                          currentStep > step.number
                            ? 'bg-green-500'
                            : 'bg-muted'
                        )}
                      />
                    ) : null}
                  </div>
                );
              })}
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {currentStep === 1 ? (
            <div>
              <h3 className="mb-4 text-lg font-semibold">Step 1: Create Your Team</h3>
              <p className="mb-6 text-sm text-muted-foreground">
                A team is where you and your colleagues will collaborate on localization projects.
              </p>
              <CreateTeamStep onNext={handleTeamCreated} />
            </div>
          ) : null}

          {currentStep === 2 && createdTeamId ? (
            <div>
              <h3 className="mb-4 text-lg font-semibold">Step 2: Invite Team Members</h3>
              <p className="mb-6 text-sm text-muted-foreground">
                Invite your colleagues to collaborate. You can also skip this step and add members later.
              </p>
              <InviteMembersStep
                teamId={createdTeamId}
                onNext={handleMembersInvited}
                onSkip={handleMembersInvited}
              />
            </div>
          ) : null}

          {currentStep === 3 && createdTeamId ? (
            <div>
              <h3 className="mb-4 text-lg font-semibold">Step 3: Create Your First Project</h3>
              <p className="mb-6 text-sm text-muted-foreground">
                Projects contain translation keys organized by languages. We've pre-filled English as your default language, but you can add more!
              </p>
              <CreateProjectStep
                teamId={createdTeamId}
                onComplete={handleProjectCreated}
              />
            </div>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
};

