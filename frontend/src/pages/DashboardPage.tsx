import { useEffect, type FC } from 'react';
import { ProjectList } from '@/components/project';
import { ActiveAgentsSection } from '@/components/github';
import { useBreadcrumbs } from '@/contexts';
import { useTeamStore } from '@/stores';

export const DashboardPage: FC = () => {
  const { setBreadcrumbs } = useBreadcrumbs();
  const { selectedTeamId } = useTeamStore();

  useEffect(() => {
    setBreadcrumbs([{ label: 'Dashboard' }]);
  }, [setBreadcrumbs]);

  return (
    <div className="flex flex-col gap-6">
      {selectedTeamId ? <ActiveAgentsSection teamId={selectedTeamId} /> : null}
      <ProjectList />
    </div>
  );
};

