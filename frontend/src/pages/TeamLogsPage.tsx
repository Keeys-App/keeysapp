import { useEffect, type FC } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@apollo/client";
import { History } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Spinner } from "@/components/ui/spinner";
import { useBreadcrumbs } from "@/contexts/BreadcrumbContext";
import { ActivityTimeline } from "@/components/activity";
import { GET_TEAM_ACTIVITY } from "@/graphql/activityLogs";
import { GET_TEAM } from "@/graphql/teams";
import type { GetTeamResponse } from "@/graphql/teams";
import type { ActivityLog } from "@/types/activity";

interface GetTeamActivityResponse {
  teamActivity: ActivityLog[];
}

export const TeamLogsPage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setBreadcrumbs } = useBreadcrumbs();

  const { data: teamData, loading: teamLoading } = useQuery<GetTeamResponse>(
    GET_TEAM,
    {
      variables: { id },
      skip: !id,
      fetchPolicy: "cache-and-network",
      nextFetchPolicy: "cache-first",
    }
  );

  const { data, loading, error, refetch } = useQuery<GetTeamActivityResponse>(
    GET_TEAM_ACTIVITY,
    {
      variables: { teamId: id, limit: 100 },
      skip: !id,
      fetchPolicy: "cache-and-network",
      nextFetchPolicy: "cache-first",
    }
  );

  const team = teamData?.team;
  const logs = data?.teamActivity || [];

  useEffect(() => {
    if (team) {
      setBreadcrumbs([
        { label: "Teams", href: "/teams" },
        { label: team.name, href: `/team/${team.id}` },
        { label: "Activity" },
      ]);
    }
  }, [team, setBreadcrumbs]);

  // Only show spinner if loading AND no cached data
  if ((teamLoading || loading) && !teamData && !data) {
    return (
      <div className="flex h-full items-center justify-center">
        <Spinner className="h-8 w-8" />
      </div>
    );
  }

  if (!team) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-destructive mb-4">Team not found</p>
          <Button
            onClick={() => {
              return navigate("/teams");
            }}
          >
            Back to Teams
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col p-6">
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-2">
          <History className="h-6 w-6 text-muted-foreground" />
          <h1 className="text-3xl font-bold">Team Activity</h1>
        </div>
        <p className="text-muted-foreground">
          Activity log for all projects in {team.name}
        </p>
      </div>

      <ActivityTimeline
        logs={logs}
        loading={loading}
        error={error}
        onRetry={() => {
          return refetch();
        }}
        showProject={true}
        showDiff={false}
      />
    </div>
  );
};
