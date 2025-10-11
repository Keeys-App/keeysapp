import { type FC, useEffect } from "react";
import { useQuery } from "@apollo/client";
import { GET_KEY_LOGS } from "@/graphql/keys";
import { formatDistanceToNow } from "date-fns";
import {
  History,
  FileText,
  Languages,
  Delete,
  Trash,
  Plus,
  Edit,
  FileDown,
  AlertCircle,
  MessageSquareHeart,
  MessageSquareX,
  MessageSquareOff,
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";
import { InlineDiff } from "./InlineDiff";

interface User {
  id: string;
  username: string;
  email: string;
}

interface KeyLog {
  id: number;
  keyId: number;
  userId: number | null;
  user: User | null;
  action: string;
  fieldName: string | null;
  language: string | null;
  oldValue: string | null;
  newValue: string | null;
  createdAt: string;
}

interface KeyLogsTimelineProps {
  keyId: string;
  limit?: number;
}

const actionLabels: Record<string, string> = {
  CREATE: "Created",
  UPDATE_KEY: "Key renamed",
  UPDATE_DESCRIPTION: "Description updated",
  UPDATE_TRANSLATION: "Translation updated",
  DELETE_TRANSLATION: "Translation deleted",
  DELETE: "Deleted",
  IMPORT: "Imported",
  REVIEW_APPROVE: "Approved",
  REVIEW_REJECT: "Rejected",
  REVIEW_DELETE: "Review revoked",
};

const actionIcons: Record<string, typeof History> = {
  CREATE: Plus,
  UPDATE_KEY: Edit,
  UPDATE_DESCRIPTION: FileText,
  UPDATE_TRANSLATION: Languages,
  DELETE_TRANSLATION: Delete,
  DELETE: Trash,
  IMPORT: FileDown,
  REVIEW_APPROVE: MessageSquareHeart,
  REVIEW_REJECT: MessageSquareX,
  REVIEW_DELETE: MessageSquareOff,
};

const actionColors: Record<string, string> = {
  CREATE: "bg-green-500/10 text-green-600",
  UPDATE_KEY: "bg-blue-500/10 text-blue-600",
  UPDATE_DESCRIPTION: "bg-blue-500/10 text-blue-600",
  UPDATE_TRANSLATION: "bg-purple-500/10 text-purple-600",
  DELETE_TRANSLATION: "bg-red-500/10 text-red-600",
  DELETE: "bg-red-500/10 text-red-600",
  IMPORT: "bg-cyan-500/10 text-cyan-600",
  REVIEW_APPROVE: "bg-green-500/10 text-green-600",
  REVIEW_REJECT: "bg-red-500/10 text-red-600",
  REVIEW_DELETE: "bg-gray-500/10 text-gray-600",
};

/**
 * Timeline component for displaying key change history
 */
export const KeyLogsTimeline: FC<KeyLogsTimelineProps> = ({
  keyId,
  limit = 50,
}) => {
  const { data, loading, error, refetch } = useQuery<{ keyLogs: KeyLog[] }>(
    GET_KEY_LOGS,
    {
      variables: { keyId, limit },
      skip: !keyId,
      fetchPolicy: 'cache-and-network',
    }
  );

  // Refetch logs when keyId changes
  useEffect(() => {
    if (keyId) {
      refetch();
    }
  }, [keyId, refetch]);

  if (loading) {
    return (
      <div className="space-y-6 pt-4">
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
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <AlertCircle className="w-12 h-12 mx-auto mb-3 text-destructive opacity-70" />
        <p className="text-muted-foreground mb-4">Failed to load history</p>
        <Button variant="outline" size="sm" onClick={() => refetch()}>
          Try again
        </Button>
      </div>
    );
  }

  const logs = data?.keyLogs || [];

  if (logs.length === 0) {
    return (
      <div className="flex items-center justify-center py-8">
        <Empty>
          <EmptyHeader>
            <EmptyMedia variant="icon">
              <History />
            </EmptyMedia>
            <EmptyTitle>No events yet</EmptyTitle>
            <EmptyDescription>
              Here you can see all events that have happened to this key over time.
            </EmptyDescription>
          </EmptyHeader>
        </Empty>
      </div>
    );
  }

  return (
    <div className="relative pt-4">
      {/* Timeline items */}
      <div className="space-y-4">
        {logs.map((log, index) => {
          const Icon = actionIcons[log.action] || History;
          const colorClass = actionColors[log.action] || "bg-gray-500/10 text-gray-600";
          const label = actionLabels[log.action] || log.action;
          const isLast = index === logs.length - 1;

          return (
            <div key={log.id} className="relative flex gap-3 pl-0">
              {/* Timeline line - show for all except last, starting from icon center */}
              {!isLast ? (
                <div className="absolute left-3 top-6 bottom-[-1rem] w-px bg-border" />
              ) : null}
              
              {/* Icon */}
              <div
                className={`flex-shrink-0 w-6 h-6 rounded-full ${colorClass} flex items-center justify-center z-10 relative`}
              >
                <Icon className="w-3.5 h-3.5" />
              </div>

              {/* Content */}
              <div className="flex-1 pb-2">
                <div className="flex items-center justify-between gap-2 mb-1 pt-0.5">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{label}</span>
                    {log.user ? (
                      <span className="text-xs text-muted-foreground">
                        by {log.user.username}
                      </span>
                    ) : null}
                  </div>
                  <span className="text-xs text-muted-foreground whitespace-nowrap">
                    {formatDistanceToNow(new Date(log.createdAt), {
                      addSuffix: true,
                    })}
                  </span>
                </div>

                {/* Action details */}
                <div className="text-sm text-muted-foreground space-y-1">
                  {log.action === "REVIEW_APPROVE" || log.action === "REVIEW_REJECT" || log.action === "REVIEW_DELETE" ? (
                    <>
                      {log.language ? (
                        <div className="text-xs text-muted-foreground/70 mb-1">
                          Language: <span className="font-mono bg-muted px-1.5 py-0.5 rounded font-medium">{log.language.toUpperCase()}</span>
                        </div>
                      ) : null}
                      {log.newValue && log.action !== "REVIEW_DELETE" ? (
                        <div className="text-sm">
                          {log.newValue}
                        </div>
                      ) : null}
                    </>
                  ) : (log.oldValue || log.newValue) ? (
                    <InlineDiff 
                      oldValue={log.oldValue || ''} 
                      newValue={log.newValue || ''}
                      language={log.language || undefined}
                    />
                  ) : null}
                  
                  {!log.oldValue && !log.newValue && log.language ? (
                    <div className="text-xs text-muted-foreground/70">
                      Language: <span className="font-mono bg-muted px-1.5 py-0.5 rounded">{log.language}</span>
                    </div>
                  ) : null}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

