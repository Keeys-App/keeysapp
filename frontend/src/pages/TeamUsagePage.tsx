import { useEffect, useState, type FC } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@apollo/client";
import { Bot, Cpu, Layers, TrendingUp, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Spinner } from "@/components/ui/spinner";
import { useBreadcrumbs } from "@/contexts/BreadcrumbContext";
import { GET_TEAM, GET_TEAM_TOKEN_USAGE } from "@/graphql/teams";
import type {
  GetTeamResponse,
  GetTeamTokenUsageResponse,
  TokenUsageBreakdownItem,
} from "@/graphql/teams";
import { cn } from "@/lib/utils";

// Human-readable labels for operation types
const OPERATION_LABELS: Record<string, string> = {
  SCAN_FILE: "File Scanning",
  TRANSLATE: "Translation",
  REPHRASE: "Rephrasing",
  SHORTEN: "Shortening",
  VARIANTS: "Generating Variants",
};

// Human-readable labels for AI providers
const PROVIDER_LABELS: Record<string, string> = {
  ANTHROPIC: "Anthropic",
  OPENAI: "OpenAI",
};

const formatNumber = (num: number): string => {
  if (num >= 1_000_000) {
    return `${(num / 1_000_000).toFixed(1)}M`;
  }
  if (num >= 1_000) {
    return `${(num / 1_000).toFixed(1)}K`;
  }
  return num.toLocaleString();
};

interface UsageBarProps {
  items: TokenUsageBreakdownItem[];
  total: number;
  getLabel?: (name: string) => string;
}

const UsageBar: FC<UsageBarProps> = ({ items, total, getLabel }) => {
  if (items.length === 0 || total === 0) {
    return (
      <div className="text-sm text-muted-foreground text-center py-4">
        No usage data
      </div>
    );
  }

  // Sort by tokens descending
  const sorted = [...items].sort((a, b) => b.tokens - a.tokens);

  // Generate colors
  const colors = [
    "bg-blue-500",
    "bg-emerald-500",
    "bg-violet-500",
    "bg-amber-500",
    "bg-rose-500",
    "bg-cyan-500",
    "bg-pink-500",
    "bg-indigo-500",
  ];

  return (
    <div className="space-y-3">
      {/* Stacked bar */}
      <div className="h-4 rounded-full overflow-hidden flex bg-muted">
        {sorted.map((item, index) => {
          const percentage = (item.tokens / total) * 100;
          if (percentage < 0.5) {
            return null;
          }
          return (
            <div
              key={item.name}
              className={cn(colors[index % colors.length], "transition-all")}
              style={{ width: `${percentage}%` }}
              title={`${getLabel ? getLabel(item.name) : item.name}: ${formatNumber(item.tokens)} tokens (${percentage.toFixed(1)}%)`}
            />
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-x-4 gap-y-2">
        {sorted.map((item, index) => {
          const percentage = (item.tokens / total) * 100;
          return (
            <div key={item.name} className="flex items-center gap-2 text-sm">
              <div
                className={cn(
                  "w-3 h-3 rounded-sm",
                  colors[index % colors.length]
                )}
              />
              <span className="text-muted-foreground">
                {getLabel ? getLabel(item.name) : item.name}:
              </span>
              <span className="font-medium">
                {formatNumber(item.tokens)} ({percentage.toFixed(1)}%)
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export const TeamUsagePage: FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { setBreadcrumbs } = useBreadcrumbs();
  const [days, setDays] = useState<number>(30);

  const { data: teamData, loading: teamLoading } = useQuery<GetTeamResponse>(
    GET_TEAM,
    {
      variables: { id },
      skip: !id,
      fetchPolicy: "cache-and-network",
      nextFetchPolicy: "cache-first",
    }
  );

  const { data, loading, refetch } = useQuery<GetTeamTokenUsageResponse>(
    GET_TEAM_TOKEN_USAGE,
    {
      variables: { teamId: id, days },
      skip: !id,
      fetchPolicy: "cache-and-network",
      nextFetchPolicy: "cache-first",
    }
  );

  const team = teamData?.team;
  const usage = data?.teamTokenUsage;

  useEffect(() => {
    if (team) {
      setBreadcrumbs([
        { label: "Teams", href: "/teams" },
        { label: team.name, href: `/team/${team.id}` },
        { label: "AI Usage" },
      ]);
    }
  }, [team, setBreadcrumbs]);

  useEffect(() => {
    if (id) {
      refetch({ teamId: id, days });
    }
  }, [days, id, refetch]);

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
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 mb-2">
            <Bot className="h-6 w-6 text-muted-foreground" />
            <h1 className="text-3xl font-bold">AI Token Usage</h1>
          </div>
          <Select
            value={days.toString()}
            onValueChange={(value) => {
              return setDays(parseInt(value, 10));
            }}
          >
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">Today</SelectItem>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <p className="text-muted-foreground">
          AI token consumption for {team.name}
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Tokens</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {usage ? formatNumber(usage.totalTokens) : "—"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Input + Output tokens
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Input Tokens</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {usage ? formatNumber(usage.totalInputTokens) : "—"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Tokens sent to AI
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Output Tokens</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground rotate-180" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {usage ? formatNumber(usage.totalOutputTokens) : "—"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Tokens received from AI
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Operations</CardTitle>
            <Layers className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {usage ? formatNumber(usage.operationsCount) : "—"}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Total AI API calls
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Breakdown Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Operation */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-muted-foreground" />
              <CardTitle>By Operation Type</CardTitle>
            </div>
            <CardDescription>Token usage by AI operation</CardDescription>
          </CardHeader>
          <CardContent>
            <UsageBar
              items={usage?.byOperation || []}
              total={usage?.totalTokens || 0}
              getLabel={(name) => OPERATION_LABELS[name] || name}
            />
          </CardContent>
        </Card>

        {/* By Provider */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-muted-foreground" />
              <CardTitle>By AI Provider</CardTitle>
            </div>
            <CardDescription>Token usage by AI provider</CardDescription>
          </CardHeader>
          <CardContent>
            <UsageBar
              items={usage?.byProvider || []}
              total={usage?.totalTokens || 0}
              getLabel={(name) => PROVIDER_LABELS[name] || name}
            />
          </CardContent>
        </Card>

        {/* By Model */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Cpu className="h-5 w-5 text-muted-foreground" />
              <CardTitle>By Model</CardTitle>
            </div>
            <CardDescription>Token usage by AI model</CardDescription>
          </CardHeader>
          <CardContent>
            <UsageBar
              items={usage?.byModel || []}
              total={usage?.totalTokens || 0}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

