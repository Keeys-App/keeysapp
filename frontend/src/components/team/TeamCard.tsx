import { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import type { Team } from '@/graphql/teams';

interface TeamCardProps {
  team: Team;
}

export const TeamCard: FC<TeamCardProps> = ({ team }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/team/${team.id}`);
  };

  return (
    <Card
      className="cursor-pointer transition-all hover:shadow-md hover:border-primary/50"
      onClick={handleClick}
    >
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            <Users className="h-5 w-5 text-muted-foreground" />
            <CardTitle>{team.name}</CardTitle>
          </div>
          {team.canManage ? (
            <Badge variant="secondary">Admin</Badge>
          ) : null}
        </div>
        {team.description ? (
          <CardDescription>{team.description}</CardDescription>
        ) : null}
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            <span>{team.membersCount} members</span>
          </div>
          <span>•</span>
          <span>Owner: {team.owner.username}</span>
        </div>
      </CardContent>
    </Card>
  );
};

