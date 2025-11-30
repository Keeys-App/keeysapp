import { type FC } from 'react';
import { History, AlertCircle } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from '@/components/ui/empty';
import { Item } from '@/components/ui/item';
import { ActivityItem } from './ActivityItem';
import type { ActivityLog } from '@/types/activity';

interface ActivityTimelineProps {
  logs: ActivityLog[];
  loading?: boolean;
  error?: Error | null;
  onRetry?: () => void;
  showProject?: boolean;
  showDiff?: boolean;
}

/**
 * Timeline component for displaying activity logs
 */
export const ActivityTimeline: FC<ActivityTimelineProps> = ({
  logs,
  loading = false,
  error = null,
  onRetry,
  showProject = false,
  showDiff = true,
}) => {
  let content: React.ReactNode | null = null;

  if (loading) {
    content = (
      <div className="space-y-6 mb-2">
        {Array.from({ length: 10 }).map((_, i) => {
          return (
            <div key={i} className="flex gap-3">
              <Skeleton className="w-6 h-6 rounded-full flex-shrink-0" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-full" />
              </div>
            </div>
          );
        })}
      </div>
    );
  } else if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 mx-auto mb-3 text-destructive opacity-70" />
        <p className="text-muted-foreground mb-4">Failed to load activity</p>
        {onRetry ? (
          <Button variant="outline" size="sm" onClick={onRetry}>
            Try again
          </Button>
        ) : null}
      </div>
    );
  } else if (logs.length === 0) {
    content = (
      <div className="flex items-center justify-center py-8">
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <History />
            </EmptyMedia>
            <EmptyTitle>No activity yet</EmptyTitle>
            <EmptyDescription>
              Activity will appear here as team members make changes.
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
      </div>
    );
  } else {
    content = (
      <div className="space-y-4">
        {logs.map((log, index) => {
          return (
            <ActivityItem
              key={log.id}
              log={log}
              isLast={index === logs.length - 1}
              showProject={showProject}
              showDiff={showDiff}
            />
          );
        })}
      </div>
    );
  }

  return (
    <div className="relative block">
      {content}
    </div>
  );
};

