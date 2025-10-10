import { type FC, useEffect } from "react";
import { useQuery } from "@apollo/client";
import { GET_KEY_LOGS } from "@/graphql/keys";
import { formatDistanceToNow } from "date-fns";
import {
  History,
  FileText,
  Languages,
  Trash2,
  Plus,
  Edit,
} from "lucide-react";
import { Skeleton } from "@/components/ui/skeleton";

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
};

const actionIcons: Record<string, typeof History> = {
  CREATE: Plus,
  UPDATE_KEY: Edit,
  UPDATE_DESCRIPTION: FileText,
  UPDATE_TRANSLATION: Languages,
  DELETE_TRANSLATION: Trash2,
  DELETE: Trash2,
};

const actionColors: Record<string, string> = {
  CREATE: "bg-green-500",
  UPDATE_KEY: "bg-blue-500",
  UPDATE_DESCRIPTION: "bg-blue-500",
  UPDATE_TRANSLATION: "bg-purple-500",
  DELETE_TRANSLATION: "bg-orange-500",
  DELETE: "bg-red-500",
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
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map((i) => {
          return (
            <div key={i} className="flex gap-4">
              <Skeleton className="w-8 h-8 rounded-full flex-shrink-0" />
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
      <div className="text-center py-8 text-muted-foreground">
        <p>Failed to load history</p>
      </div>
    );
  }

  const logs = data?.keyLogs || [];

  if (logs.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        <History className="w-12 h-12 mx-auto mb-2 opacity-50" />
        <p>No history yet</p>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-4 top-4 bottom-4 w-px bg-border" />

      {/* Timeline items */}
      <div className="space-y-6">
        {logs.map((log, index) => {
          const Icon = actionIcons[log.action] || History;
          const colorClass = actionColors[log.action] || "bg-gray-500";
          const label = actionLabels[log.action] || log.action;

          return (
            <div key={log.id} className="relative flex gap-4 pl-0">
              {/* Icon */}
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full ${colorClass} flex items-center justify-center z-10`}
              >
                <Icon className="w-4 h-4 text-white" />
              </div>

              {/* Content */}
              <div className="flex-1 pb-2">
                <div className="flex items-center justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm">{label}</span>
                    {log.user ? (
                      <span className="text-xs text-muted-foreground">
                        by {log.user.username}
                      </span>
                    ) : null}
                  </div>
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(log.createdAt), {
                      addSuffix: true,
                    })}
                  </span>
                </div>

                {/* Action details */}
                <div className="text-sm text-muted-foreground space-y-1">
                  {log.language ? (
                    <div>
                      <span className="font-mono bg-muted px-1.5 py-0.5 rounded text-xs">
                        {log.language}
                      </span>
                    </div>
                  ) : null}

                  {log.oldValue && log.newValue ? (
                    <div className="space-y-1 mt-2">
                      <div className="text-xs text-muted-foreground/70">
                        Old:
                      </div>
                      <div className="bg-red-500/10 border border-red-500/20 rounded px-2 py-1 text-xs font-mono break-all line-through">
                        {log.oldValue}
                      </div>
                      <div className="text-xs text-muted-foreground/70">
                        New:
                      </div>
                      <div className="bg-green-500/10 border border-green-500/20 rounded px-2 py-1 text-xs font-mono break-all">
                        {log.newValue}
                      </div>
                    </div>
                  ) : null}

                  {log.oldValue && !log.newValue ? (
                    <div className="space-y-1 mt-2">
                      <div className="text-xs text-muted-foreground/70">
                        Deleted:
                      </div>
                      <div className="bg-red-500/10 border border-red-500/20 rounded px-2 py-1 text-xs font-mono break-all line-through">
                        {log.oldValue}
                      </div>
                    </div>
                  ) : null}

                  {!log.oldValue && log.newValue ? (
                    <div className="space-y-1 mt-2">
                      <div className="text-xs text-muted-foreground/70">
                        Created:
                      </div>
                      <div className="bg-green-500/10 border border-green-500/20 rounded px-2 py-1 text-xs font-mono break-all">
                        {log.newValue}
                      </div>
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

