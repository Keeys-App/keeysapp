import { Fragment, useMemo, type FC } from 'react';
import { Outlet, Link } from 'react-router-dom';
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
import { useSavingStore, useLayoutStore, useTeamStore } from '@/stores';
import { Spinner } from '@/components/ui/spinner';
import { Button } from '@/components/ui/button';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { PanelRightClose, PanelRightOpen } from 'lucide-react';
import { TeamSwitcher } from '@/components/team/TeamSwitcher';

export const Layout: FC = () => {
  const { breadcrumbs } = useBreadcrumbs();
  const { isSaving, savingMessage } = useSavingStore();
  const { isPanelOpen, showPanelToggle, togglePanel } = useLayoutStore();
  const { selectedTeamId, setSelectedTeamId } = useTeamStore();

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
        {isSaving ? (
          <footer className="bg-background h-10 border-t box-border sticky z-10 bottom-0 flex shrink-0 items-center gap-2 px-4 py-2">
            <Spinner className="h-4 w-4" />
            <span className="text-sm text-muted-foreground">{savingMessage}</span>
          </footer>
        ) : null}
      </SidebarInset>
    </SidebarProvider>
  );
};
