import { type FC } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Settings, GitBranch, Search } from 'lucide-react';
import { cn } from '@/lib/utils';
import { PATHS } from '@/constants/paths';

interface ProjectSettingsTabsProps {
  projectId: string;
  hasRepository?: boolean;
}

interface Tab {
  id: string;
  label: string;
  icon: typeof Settings;
  path: string;
  disabled?: boolean;
}

export const ProjectSettingsTabs: FC<ProjectSettingsTabsProps> = ({
  projectId,
  hasRepository = false,
}) => {
  const location = useLocation();
  const navigate = useNavigate();

  const tabs: Tab[] = [
    {
      id: 'general',
      label: 'General',
      icon: Settings,
      path: PATHS.PROJECT_EDIT.replace(':id', projectId),
    },
    {
      id: 'repository',
      label: 'Repository',
      icon: GitBranch,
      path: PATHS.PROJECT_REPOSITORY.replace(':id', projectId),
    },
    {
      id: 'scanner',
      label: 'Find Keys',
      icon: Search,
      path: PATHS.PROJECT_SCANNER.replace(':id', projectId),
      disabled: !hasRepository,
    },
  ];

  const currentTab = tabs.find((tab) => location.pathname === tab.path)?.id || 'general';

  return (
    <div className="border-b mb-6">
      <nav className="flex gap-4" aria-label="Project settings">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = currentTab === tab.id;
          const isDisabled = tab.disabled;

          return (
            <button
              key={tab.id}
              onClick={() => {
                if (!isDisabled) {
                  navigate(tab.path);
                }
              }}
              disabled={isDisabled}
              className={cn(
                'flex items-center gap-2 px-1 py-3 text-sm font-medium border-b-2 -mb-px transition-colors',
                isActive
                  ? 'border-primary text-primary'
                  : 'border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/30',
                isDisabled && 'opacity-50 cursor-not-allowed'
              )}
            >
              <Icon className="h-4 w-4" />
              {tab.label}
            </button>
          );
        })}
      </nav>
    </div>
  );
};

