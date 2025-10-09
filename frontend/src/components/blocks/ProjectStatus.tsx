import type { FC } from 'react';
import { TrendingUp, Archive, FileText, type LucideIcon } from 'lucide-react';
import { ProjectStatus as ProjectStatusEnum } from '@/types/project';

interface ProjectStatusProps {
  status: string;
  className?: string;
  showIcon?: boolean;
  showLabel?: boolean;
}

interface StatusInfo {
  label: string;
  icon: LucideIcon;
  className: string;
}

/**
 * Get status information based on project status.
 */
export const getProjectStatusInfo = (status: string): StatusInfo => {
  switch (status) {
    case ProjectStatusEnum.ACTIVE:
      return {
        label: 'Active',
        icon: TrendingUp,
        className: 'text-emerald-600 dark:text-emerald-400',
      };
    case ProjectStatusEnum.ARCHIVED:
      return {
        label: 'Archived',
        icon: Archive,
        className: 'text-gray-500',
      };
    case ProjectStatusEnum.DRAFT:
      return {
        label: 'Draft',
        icon: FileText,
        className: 'text-amber-600 dark:text-amber-400',
      };
    default:
      return {
        label: status,
        icon: FileText,
        className: 'text-gray-500',
      };
  }
};

/**
 * ProjectStatus component - displays project status with icon and label.
 * Can be used independently or as part of project cards.
 */
export const ProjectStatus: FC<ProjectStatusProps> = ({
  status,
  className = '',
  showIcon = true,
  showLabel = true,
}) => {
  const statusInfo = getProjectStatusInfo(status);
  const StatusIcon = statusInfo.icon;

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {showIcon ? <StatusIcon className={`h-4 w-4 ${statusInfo.className}`} /> : null}
      {showLabel ? (
        <span className={`text-sm font-medium ${statusInfo.className}`}>
          {statusInfo.label}
        </span>
      ) : null}
    </div>
  );
};

