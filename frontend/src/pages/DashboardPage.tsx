import { useEffect, type FC } from 'react';
import { ProjectList } from '@/components/project';
import { useBreadcrumbs } from '@/contexts';

export const DashboardPage: FC = () => {
  const { setBreadcrumbs } = useBreadcrumbs();

  useEffect(() => {
    setBreadcrumbs([{ label: 'Dashboard' }]);
  }, [setBreadcrumbs]);

  return <ProjectList />;
};

