import { type FC, useMemo, useEffect } from 'react';
import { useQuery, useMutation } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { Bot, Search, Code, Clock, AlertCircle, CheckCircle2, XCircle, Loader2, ExternalLink, Square, Trash2 } from 'lucide-react';
import { toast } from 'sonner';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/components/ui/tooltip';
import { cn } from '@/lib/utils';
import { PATHS } from '@/constants/paths';
import { useSaving, useSavingStore } from '@/stores';
import {
  TEAM_ACTIVE_AGENTS_QUERY,
  CANCEL_SCAN_MUTATION,
  CANCEL_PR_CREATION_MUTATION,
  DELETE_SCAN_SESSION_MUTATION,
  AgentType,
  type ActiveAgent,
  type TeamActiveAgentsData,
} from '@/graphql/scanner';

interface ActiveAgentsSectionProps {
  teamId: string;
}

/**
 * Format execution time in human-readable format
 */
function formatExecutionTime(seconds: number): string {
  if (seconds < 60) {
    return `${seconds}s`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  if (minutes < 60) {
    return remainingSeconds > 0 ? `${minutes}m ${remainingSeconds}s` : `${minutes}m`;
  }
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes > 0 ? `${hours}h ${remainingMinutes}m` : `${hours}h`;
}

/**
 * Get agent type label and icon
 */
function getAgentInfo(agentType: AgentType) {
  switch (agentType) {
    case AgentType.SCANNING:
      return {
        label: 'Scanning Agent',
        icon: Search,
        description: 'Finding hardcoded strings',
      };
    case AgentType.CODING:
      return {
        label: 'Coding Agent',
        icon: Code,
        description: 'Creating pull request',
      };
    default:
      return {
        label: 'Agent',
        icon: Bot,
        description: 'Processing',
      };
  }
}

/**
 * Get status badge variant and icon
 */
function getStatusInfo(status: string) {
  switch (status.toLowerCase()) {
    case 'running':
      return {
        variant: 'default' as const,
        icon: Loader2,
        className: 'bg-blue-500/10 text-blue-700 border-blue-500/20',
        iconClassName: 'animate-spin',
      };
    case 'pending':
      return {
        variant: 'secondary' as const,
        icon: Clock,
        className: 'bg-yellow-500/10 text-yellow-700 border-yellow-500/20',
        iconClassName: '',
      };
    case 'completed':
      return {
        variant: 'default' as const,
        icon: CheckCircle2,
        className: 'bg-green-500/10 text-green-700 border-green-500/20',
        iconClassName: '',
      };
    case 'failed':
      return {
        variant: 'destructive' as const,
        icon: XCircle,
        className: 'bg-red-500/10 text-red-700 border-red-500/20',
        iconClassName: '',
      };
    case 'cancelled':
      return {
        variant: 'outline' as const,
        icon: XCircle,
        className: 'bg-gray-500/10 text-gray-700 border-gray-500/20',
        iconClassName: '',
      };
    default:
      return {
        variant: 'outline' as const,
        icon: AlertCircle,
        className: '',
        iconClassName: '',
      };
  }
}

export const ActiveAgentsSection: FC<ActiveAgentsSectionProps> = ({ teamId }) => {
  const navigate = useNavigate();
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const { data, loading, error, refetch } = useQuery<TeamActiveAgentsData>(TEAM_ACTIVE_AGENTS_QUERY, {
    variables: { teamId },
    skip: !teamId,
    pollInterval: 5000, // Poll every 5 seconds for updates
    fetchPolicy: 'cache-and-network',
  });

  // Mutations
  const [cancelScan, { data: cancelScanData, error: cancelScanError }] = useMutation(CANCEL_SCAN_MUTATION);
  const [cancelPr, { data: cancelPrData, error: cancelPrError }] = useMutation(CANCEL_PR_CREATION_MUTATION);
  const [deleteSession, { data: deleteData, error: deleteError }] = useMutation(DELETE_SCAN_SESSION_MUTATION);

  // Handle mutation results
  useEffect(() => {
    if (cancelScanData?.cancelScan?.success) {
      toast('Scan cancelled successfully');
      refetch();
    }
  }, [cancelScanData, refetch]);

  useEffect(() => {
    if (cancelPrData?.cancelPrCreation?.success) {
      toast('PR creation cancelled');
      refetch();
    }
  }, [cancelPrData, refetch]);

  useEffect(() => {
    if (deleteData?.deleteScanSession?.success) {
      toast('Session deleted');
      refetch();
    }
  }, [deleteData, refetch]);

  // Handle errors
  useEffect(() => {
    if (cancelScanError) {
      toast('Failed to cancel scan');
    }
  }, [cancelScanError]);

  useEffect(() => {
    if (cancelPrError) {
      toast('Failed to cancel PR creation');
    }
  }, [cancelPrError]);

  useEffect(() => {
    if (deleteError) {
      toast('Failed to delete session');
    }
  }, [deleteError]);

  // Filter to show only active (running/pending) agents, plus recent completed/failed (last 10)
  const agents = useMemo(() => {
    if (!data?.teamActiveAgents) {
      return [];
    }
    
    const activeAgents = data.teamActiveAgents.filter((agent) => {
      return ['running', 'pending'].includes(agent.status.toLowerCase());
    });
    
    const recentAgents = data.teamActiveAgents
      .filter((agent) => {
        return !['running', 'pending'].includes(agent.status.toLowerCase());
      })
      .slice(0, 10);
    
    return [...activeAgents, ...recentAgents];
  }, [data]);

  // Don't show section on error
  if (error) {
    return null;
  }

  const handleProjectClick = (projectId: string) => {
    navigate(PATHS.PROJECT_SCANNER.replace(':id', projectId));
  };

  const handleStop = async (agent: ActiveAgent) => {
    await withSaving(async () => {
      if (agent.agentType === AgentType.CODING) {
        await cancelPr({ variables: { scanSessionId: agent.id } });
      } else {
        await cancelScan({ variables: { scanSessionId: agent.id } });
      }
    }, 'Stopping agent...');
  };

  const handleDelete = async (agent: ActiveAgent) => {
    await withSaving(async () => {
      await deleteSession({ variables: { scanSessionId: agent.id } });
    }, 'Deleting session...');
  };

  const isRunning = (status: string) => {
    return ['running', 'pending'].includes(status.toLowerCase());
  };

  const canDelete = (status: string) => {
    return ['completed', 'failed', 'cancelled'].includes(status.toLowerCase());
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <Bot className="h-5 w-5 text-muted-foreground" />
          <div>
            <CardTitle className="text-lg">Active Agents</CardTitle>
            <CardDescription>
              AI agents scanning repositories and creating pull requests
            </CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {loading && agents.length === 0 ? (
          <div className="flex items-center justify-center py-8">
            <Spinner className="h-6 w-6" />
          </div>
        ) : agents.length === 0 ? (
          <div className="flex items-center justify-center py-8 text-muted-foreground">
            No active agents
          </div>
        ) : (
          <TooltipProvider>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Project</TableHead>
                  <TableHead>Agent</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="w-[120px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {agents.map((agent) => {
                  const agentInfo = getAgentInfo(agent.agentType);
                  const statusInfo = getStatusInfo(agent.status);
                  const StatusIcon = statusInfo.icon;
                  const AgentIcon = agentInfo.icon;

                  return (
                    <TableRow key={agent.id}>
                      <TableCell>
                        <span className="font-medium">{agent.projectName}</span>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <AgentIcon className="h-4 w-4 text-muted-foreground" />
                          <span>{agentInfo.label}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {agent.progress ? (
                          <span className="text-sm text-muted-foreground">{agent.progress}</span>
                        ) : (
                          <span className="text-sm text-muted-foreground">—</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          {formatExecutionTime(agent.executionTimeSeconds)}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant={statusInfo.variant} className={statusInfo.className}>
                          <StatusIcon className={cn('mr-1 h-3 w-3', statusInfo.iconClassName)} />
                          {agent.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1">
                          <Tooltip>
                            <TooltipTrigger asChild>
                              <Button
                                variant="ghost"
                                size="icon"
                                className="h-8 w-8"
                                onClick={() => {
                                  return handleProjectClick(agent.projectId);
                                }}
                              >
                                <ExternalLink className="h-4 w-4" />
                              </Button>
                            </TooltipTrigger>
                            <TooltipContent>View details</TooltipContent>
                          </Tooltip>
                          
                          {isRunning(agent.status) ? (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-orange-600 hover:text-orange-700 hover:bg-orange-100"
                                  onClick={() => {
                                    return handleStop(agent);
                                  }}
                                  disabled={isSaving}
                                >
                                  <Square className="h-4 w-4" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Stop agent</TooltipContent>
                            </Tooltip>
                          ) : null}
                          
                          {canDelete(agent.status) ? (
                            <Tooltip>
                              <TooltipTrigger asChild>
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  className="h-8 w-8 text-destructive hover:text-destructive hover:bg-destructive/10"
                                  onClick={() => {
                                    return handleDelete(agent);
                                  }}
                                  disabled={isSaving}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              </TooltipTrigger>
                              <TooltipContent>Delete session</TooltipContent>
                            </Tooltip>
                          ) : null}
                        </div>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TooltipProvider>
        )}
      </CardContent>
    </Card>
  );
};
