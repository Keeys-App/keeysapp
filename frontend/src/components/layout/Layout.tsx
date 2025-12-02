import { Fragment, useMemo, useEffect, type FC } from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { useQuery } from '@apollo/client';
import { AppSidebar } from './AppSidebar';
import { SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';
import { Separator } from '@/components/ui/separator';
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';
import { useBreadcrumbs } from '@/contexts';
import { useLayoutStore, useTeamStore, useOnboardingStore } from '@/stores';
import { useLanguagesInit } from '@/hooks/useLanguagesInit';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { PanelRightClose, PanelRightOpen } from 'lucide-react';
import { TeamSwitcher } from '@/components/team/TeamSwitcher';
import { SavingIndicator } from './SavingIndicator';
import { PATHS } from '@/constants/paths';
import { GET_TEAMS, type GetTeamsResponse } from '@/graphql/teams';

export const Layout: FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { breadcrumbs } = useBreadcrumbs();
  const { isPanelOpen, showPanelToggle, togglePanel } = useLayoutStore();
  const { selectedTeamId, setSelectedTeamId } = useTeamStore();
  const { isOnboardingComplete } = useOnboardingStore();
  
  // Initialize languages from API (single source of truth)
  useLanguagesInit();

  // Fetch teams to check if user has any teams
  const { data: teamsData, loading: teamsLoading } = useQuery<GetTeamsResponse>(GET_TEAMS, {
    fetchPolicy: 'cache-and-network',
    nextFetchPolicy: 'cache-first',
  });

  const teams = teamsData?.teams || [];

  // Redirect to onboarding if not completed
  useEffect(() => {
    if (!isOnboardingComplete) {
      navigate(PATHS.ONBOARDING, { replace: true });
    }
  }, [isOnboardingComplete, navigate]);

  // Redirect to teams page if user has no teams (except when on team create page)
  useEffect(() => {
    if (!teamsLoading && teams.length === 0) {
      // Allow access to team create page
      if (location.pathname !== PATHS.TEAM_CREATE && location.pathname !== PATHS.TEAMS) {
        navigate(PATHS.TEAMS, { replace: true });
      }
    }
  }, [teamsLoading, teams.length, location.pathname, navigate]);

  // Auto-select first team if no team selected or selected team doesn't exist
  useEffect(() => {
    if (!teamsLoading && teams.length > 0) {
      const selectedTeamExists = teams.some((team) => {
        return team.id === selectedTeamId;
      });
      
      if (!selectedTeamId || !selectedTeamExists) {
        setSelectedTeamId(teams[0].id);
      }
    }
  }, [teamsLoading, teams, selectedTeamId, setSelectedTeamId]);

  const getBreadcrumbs = useMemo(() => {
    return () => {
    if (breadcrumbs.length === 0) {
      return (
        <BreadcrumbItem>
          <BreadcrumbPage>Dashboard</BreadcrumbPage>
        </BreadcrumbItem>
      );
    }

    return breadcrumbs.map((item, index) => {
      const isLast = index === breadcrumbs.length - 1;

      return (
        <Fragment key={`breadcrumb-${index}`}>
          {index > 0 ? <BreadcrumbSeparator className="hidden md:block" /> : null}
          <BreadcrumbItem className={index > 0 ? 'hidden md:block' : ''}>
            {isLast || !item.href ? (
              <BreadcrumbPage>{item.label}</BreadcrumbPage>
            ) : (
              <BreadcrumbLink asChild>
                <Link to={item.href}>{item.label}</Link>
              </BreadcrumbLink>
            )}
          </BreadcrumbItem>
        </Fragment>
      );
    });
    };
  }, [breadcrumbs]);

  return (
    <SidebarProvider defaultOpen={false}>
      <AppSidebar />
      <SidebarInset>
        <header className="bg-background h-12 border-b box-border sticky z-10 top-0 flex shrink-0 items-center gap-3 px-4 py-3.5">
          {/* <SidebarTrigger className="-ml-1" /> */}
          {/* <Separator orientation="vertical" className="mr-2 h-4" /> */}
          
          <TeamSwitcher
            selectedTeamId={selectedTeamId}
            onTeamChange={setSelectedTeamId}
          />
          
          <Breadcrumb>
            <BreadcrumbList>{getBreadcrumbs()}</BreadcrumbList>
          </Breadcrumb>
          
          {showPanelToggle ? (
            <div className="ml-auto">
              <TooltipProvider>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="cursor-pointer h-7 w-7 p-0"
                      onClick={togglePanel}
                    >
                      {isPanelOpen ? (
                        <PanelRightClose className="h-3.5 w-3.5" />
                      ) : (
                        <PanelRightOpen className="h-3.5 w-3.5" />
                      )}
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent>
                    {isPanelOpen ? 'Hide management panel' : 'Show management panel'}
                  </TooltipContent>
                </Tooltip>
              </TooltipProvider>
            </div>
          ) : null}
        </header>
        <div className="flex flex-1 flex-col">
          <Outlet />
        </div>
        <SavingIndicator />
      </SidebarInset>
    </SidebarProvider>
  );
};
