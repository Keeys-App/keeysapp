import { type FC } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, MoreHorizontal, Settings, Eye } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import type { Team } from '@/graphql/teams';

interface TeamCardProps {
  team: Team;
}

export const TeamCard: FC<TeamCardProps> = ({ team }) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/team/${team.id}`);
  };

  const handleViewClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigate(`/team/${team.id}`);
  };

  const handleEditClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigate(`/team/${team.id}/edit`);
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
          <div className="flex items-center gap-2">
            {team.canManage ? (
              <Badge variant="secondary">Admin</Badge>
            ) : null}
            <DropdownMenu>
              <DropdownMenuTrigger asChild onClick={(e) => {
                return e.stopPropagation();
              }}>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={handleViewClick}>
                  <Eye className="mr-2 h-4 w-4" />
                  View Team
                </DropdownMenuItem>
                {team.canManage ? (
                  <DropdownMenuItem onClick={handleEditClick}>
                    <Settings className="mr-2 h-4 w-4" />
                    Team Settings
                  </DropdownMenuItem>
                ) : null}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
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

