import { type FC, useEffect } from 'react';
import { ProjectForm } from '@/components/project';
import { useBreadcrumbs } from '@/contexts';
import { PATHS } from '@/constants/paths';

export const CreateProjectPage: FC = () => {
  const { setBreadcrumbs } = useBreadcrumbs();

  useEffect(() => {
    setBreadcrumbs([
      { label: 'Dashboard', href: PATHS.DASHBOARD },
      { label: 'Create Project' },
    ]);
  }, [setBreadcrumbs]);

  return <ProjectForm mode="create" />;
};

