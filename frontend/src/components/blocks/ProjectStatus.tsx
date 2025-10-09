import type { FC } from "react";
import { ProjectStatus as ProjectStatusEnum } from "@/types/project";

interface ProjectStatusProps {
  status: string;
  className?: string;
  showIcon?: boolean;
  showLabel?: boolean;
}

interface StatusInfo {
  label: string;
  className: string;
}

/**
 * Get status information based on project status.
 */
export const getProjectStatusInfo = (status: string): StatusInfo => {
  switch (status) {
    case ProjectStatusEnum.ACTIVE:
      return {
        label: "Active",
        className: "text-emerald-600 dark:text-emerald-400",
      };
    case ProjectStatusEnum.ARCHIVED:
      return {
        label: "Archived",
        className: "text-gray-500",
      };
    case ProjectStatusEnum.DRAFT:
      return {
        label: "Draft",
        className: "text-gray-500",
      };
    default:
      return {
        label: status,
        className: "text-gray-500",
      };
  }
};

/**
 * ProjectStatus component - displays project status with icon and label.
 * Can be used independently or as part of project cards.
 */
export const ProjectStatus: FC<ProjectStatusProps> = ({
  status,
  className = "",
  showLabel = true,
}) => {
  const statusInfo = getProjectStatusInfo(status);

  return (
    <div className={`flex items-center gap-1 ${className}`}>
      {showLabel ? (
        <span className={`text-sm font-medium ${statusInfo.className}`}>
          {statusInfo.label}
        </span>
      ) : null}
    </div>
  );
};
