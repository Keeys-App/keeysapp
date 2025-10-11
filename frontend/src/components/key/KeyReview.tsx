import { type FC, useState, useEffect } from "react";
import { useMutation, useQuery } from "@apollo/client";
import { APPROVE_KEY, REJECT_KEY, DELETE_REVIEW, GET_KEY_LOGS, GET_PROJECT_KEYS, GET_KEY } from "@/graphql/keys";
import type { TranslationKey, ReviewStatus } from "@/types/translationKey";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { useSaving, useSavingStore } from "@/stores";
import { toast } from "sonner";
import { Check, X, Trash2, Clock, CheckCircle, XCircle, FileText } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface KeyReviewProps {
  selectedKey: TranslationKey;
  projectId: string;
}

const reviewStatusConfig: Record<ReviewStatus, { label: string; icon: typeof Clock; color: string }> = {
  NOT_REVIEWED: { label: "Not Reviewed", icon: FileText, color: "text-muted-foreground" },
  PENDING: { label: "Pending", icon: Clock, color: "text-yellow-600" },
  APPROVED: { label: "Approved", icon: CheckCircle, color: "text-green-600" },
  REJECTED: { label: "Rejected", icon: XCircle, color: "text-red-600" },
};

const reviewStatusBadgeVariant: Record<ReviewStatus, "default" | "secondary" | "destructive" | "outline"> = {
  NOT_REVIEWED: "secondary",
  PENDING: "outline",
  APPROVED: "default",
  REJECTED: "destructive",
};

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

/**
 * Component for reviewing translation keys
 */
export const KeyReview: FC<KeyReviewProps> = ({ selectedKey, projectId }) => {
  const [comment, setComment] = useState("");
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Get current key data from cache
  const { data: keyData } = useQuery(GET_KEY, {
    variables: { id: selectedKey.id },
    fetchPolicy: "cache-first",
  });

  // Use current key data from cache or fallback to prop
  const currentKey = keyData?.key || selectedKey;

  // GraphQL mutations
  const [approveKey] = useMutation(APPROVE_KEY, {
    refetchQueries: [
      { query: GET_PROJECT_KEYS, variables: { projectId } },
      { query: GET_KEY_LOGS, variables: { keyId: selectedKey.id } },
      { query: GET_KEY, variables: { id: selectedKey.id } },
    ],
  });

  const [rejectKey] = useMutation(REJECT_KEY, {
    refetchQueries: [
      { query: GET_PROJECT_KEYS, variables: { projectId } },
      { query: GET_KEY_LOGS, variables: { keyId: selectedKey.id } },
      { query: GET_KEY, variables: { id: selectedKey.id } },
    ],
  });

  const [deleteReview] = useMutation(DELETE_REVIEW, {
    refetchQueries: [
      { query: GET_PROJECT_KEYS, variables: { projectId } },
      { query: GET_KEY_LOGS, variables: { keyId: selectedKey.id } },
      { query: GET_KEY, variables: { id: selectedKey.id } },
    ],
  });

  // Get review logs
  const { data: logsData, loading: logsLoading } = useQuery(GET_KEY_LOGS, {
    variables: { keyId: selectedKey.id },
    fetchPolicy: "cache-and-network",
  });

  const reviewLogs = (logsData?.keyLogs || []).filter((log: KeyLog) =>
    ["REVIEW_APPROVE", "REVIEW_REJECT", "REVIEW_DELETE"].includes(log.action)
  );

  const handleApprove = async () => {
    await withSaving(async () => {
      await approveKey({
        variables: {
          input: {
            keyId: selectedKey.id,
            comment: comment.trim() || null,
          },
        },
      });
      setComment("");
      toast("Key approved");
    }, "Approving key...");
  };

  const handleReject = async () => {
    await withSaving(async () => {
      await rejectKey({
        variables: {
          input: {
            keyId: selectedKey.id,
            comment: comment.trim() || null,
          },
        },
      });
      setComment("");
      toast("Key rejected");
    }, "Rejecting key...");
  };

  const handleDeleteReview = async () => {
    await withSaving(async () => {
      await deleteReview({
        variables: { keyId: selectedKey.id },
      });
      toast("Review deleted");
    }, "Deleting review...");
  };

  const StatusIcon = reviewStatusConfig[currentKey.reviewStatus]?.icon || Clock;
  const statusColor = reviewStatusConfig[currentKey.reviewStatus]?.color || "text-muted-foreground";
  const statusLabel = reviewStatusConfig[currentKey.reviewStatus]?.label || currentKey.reviewStatus;

  return (
    <div className="space-y-6">
      {/* Current Status */}
      <div>
        <h3 className="text-sm font-medium mb-3">Current Status</h3>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <StatusIcon className={`h-5 w-5 ${statusColor}`} />
              <span className="font-medium">{statusLabel}</span>
            </div>
            <Badge variant={reviewStatusBadgeVariant[currentKey.reviewStatus]}>
              {statusLabel}
            </Badge>
          </div>
        </Card>
      </div>

      <Separator />

      {/* Review Actions */}
      <div>
        <h3 className="text-sm font-medium mb-3">Review Actions</h3>
        <div className="space-y-3">
          <Textarea
            placeholder="Add a comment (optional)..."
            value={comment}
            onChange={(e) => {
              setComment(e.target.value);
            }}
            disabled={isSaving}
            rows={3}
          />
          <div className="flex gap-2">
            <Button
              onClick={handleApprove}
              disabled={isSaving || currentKey.reviewStatus === "APPROVED"}
              variant="default"
              className="flex-1"
            >
              <Check className="h-4 w-4 mr-2" />
              Approve
            </Button>
            <Button
              onClick={handleReject}
              disabled={isSaving || currentKey.reviewStatus === "REJECTED"}
              variant="destructive"
              className="flex-1"
            >
              <X className="h-4 w-4 mr-2" />
              Reject
            </Button>
          </div>
          {currentKey.reviewStatus !== "NOT_REVIEWED" && currentKey.reviewStatus !== "PENDING" ? (
            <Button
              onClick={handleDeleteReview}
              disabled={isSaving}
              variant="outline"
              className="w-full"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Delete Review
            </Button>
          ) : null}
        </div>
      </div>

      <Separator />

      {/* Review History */}
      <div>
        <h3 className="text-sm font-medium mb-3">Review History</h3>
        {logsLoading ? (
          <div className="text-sm text-muted-foreground">Loading history...</div>
        ) : reviewLogs.length === 0 ? (
          <div className="text-sm text-muted-foreground">No review history yet</div>
        ) : (
          <div className="space-y-3">
            {reviewLogs.map((log: KeyLog) => {
              const actionLabel = log.action === "REVIEW_APPROVE" 
                ? "Approved" 
                : log.action === "REVIEW_REJECT" 
                ? "Rejected" 
                : "Review Deleted";
              
              const actionIcon = log.action === "REVIEW_APPROVE" 
                ? CheckCircle 
                : log.action === "REVIEW_REJECT" 
                ? XCircle 
                : Trash2;
              
              const ActionIcon = actionIcon;
              
              const actionColor = log.action === "REVIEW_APPROVE" 
                ? "text-green-600" 
                : log.action === "REVIEW_REJECT" 
                ? "text-red-600" 
                : "text-muted-foreground";

              return (
                <Card key={log.id} className="p-4">
                  <div className="flex items-start gap-3">
                    <ActionIcon className={`h-5 w-5 mt-0.5 ${actionColor}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm">{actionLabel}</span>
                        <span className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(log.createdAt), { addSuffix: true })}
                        </span>
                      </div>
                      {log.user ? (
                        <div className="text-sm text-muted-foreground mb-2">
                          by {log.user.username}
                        </div>
                      ) : null}
                      {log.newValue && log.action !== "REVIEW_DELETE" ? (
                        <div className="text-sm text-muted-foreground">
                          {log.newValue}
                        </div>
                      ) : null}
                    </div>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

