import type { FC } from "react";
import type { Project } from "@/types/project";

interface ExportContentProps {
  project: Project;
}

export const ExportContent: FC<ExportContentProps> = ({ project }) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[40vh] gap-4">
      <p className="text-lg text-muted-foreground">
        Export functionality will be implemented here
      </p>
      <p className="text-sm text-muted-foreground">
        Project: {project.name}
      </p>
    </div>
  );
};

