import { type FC, useState } from "react";
import { useMutation } from "@apollo/client";
import {
  APPROVE_TRANSLATION,
  REJECT_TRANSLATION,
  DELETE_TRANSLATION_REVIEW,
  GET_PROJECT_KEYS,
  GET_KEY,
  GET_KEY_LOGS,
} from "@/graphql/keys";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Separator } from "@/components/ui/separator";
import { useSaving, useSavingStore } from "@/stores";
import { toast } from "sonner";
import type { ReviewStatus } from "@/types/translationKey";
import {
  Check,
  X,
  Trash2,
  CheckCircle,
  XCircle,
  Clock,
  FileText,
} from "lucide-react";

interface ReviewStatusButtonProps {
  keyId: string;
  language: string;
  reviewStatus: ReviewStatus;
  projectId: string;
}

const reviewStatusConfig: Record<
  ReviewStatus,
  { icon: typeof Clock; color: string }
> = {
  NOT_REVIEWED: { icon: FileText, color: "text-muted-foreground" },
  PENDING: { icon: Clock, color: "text-yellow-600" },
  APPROVED: { icon: CheckCircle, color: "text-green-600" },
  REJECTED: { icon: XCircle, color: "text-red-600" },
};

/**
 * Button with review status icon that opens popover with review actions
 */
export const ReviewStatusButton: FC<ReviewStatusButtonProps> = ({
  keyId,
  language,
  reviewStatus,
  projectId,
}) => {
  const [comment, setComment] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const StatusIcon = reviewStatusConfig[reviewStatus]?.icon || Clock;
  const statusColor =
    reviewStatusConfig[reviewStatus]?.color || "text-muted-foreground";

  // Review mutations
  const [approveTranslation] = useMutation(APPROVE_TRANSLATION, {
    refetchQueries: [
      { query: GET_PROJECT_KEYS, variables: { projectId } },
      { query: GET_KEY, variables: { id: keyId } },
      { query: GET_KEY_LOGS, variables: { keyId } },
    ],
  });

  const [rejectTranslation] = useMutation(REJECT_TRANSLATION, {
    refetchQueries: [
      { query: GET_PROJECT_KEYS, variables: { projectId } },
      { query: GET_KEY, variables: { id: keyId } },
      { query: GET_KEY_LOGS, variables: { keyId } },
    ],
  });

  const [deleteTranslationReview] = useMutation(DELETE_TRANSLATION_REVIEW, {
    refetchQueries: [
      { query: GET_PROJECT_KEYS, variables: { projectId } },
      { query: GET_KEY, variables: { id: keyId } },
      { query: GET_KEY_LOGS, variables: { keyId } },
    ],
  });

  const handleApprove = async () => {
    await withSaving(async () => {
      await approveTranslation({
        variables: {
          input: {
            keyId,
            language,
            comment: comment.trim() || null,
          },
        },
      });
      setComment("");
      setIsOpen(false);
      toast("Translation approved");
    }, "Approving...");
  };

  const handleReject = async () => {
    await withSaving(async () => {
      await rejectTranslation({
        variables: {
          input: {
            keyId,
            language,
            comment: comment.trim() || null,
          },
        },
      });
      setComment("");
      setIsOpen(false);
      toast("Translation rejected");
    }, "Rejecting...");
  };

  const handleDeleteReview = async () => {
    await withSaving(async () => {
      await deleteTranslationReview({
        variables: {
          keyId,
          language,
        },
      });
      setIsOpen(false);
      toast("Review reset");
    }, "Resetting review...");
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className={`h-6 w-6 ${statusColor} hover:bg-muted`}
          onClick={(e) => {
            e.stopPropagation();
          }}
        >
          <StatusIcon className="h-4 w-4" />
        </Button>
      </PopoverTrigger>
      <PopoverContent
        className="w-64 p-3"
        align="start"
        onClick={(e) => {
          e.stopPropagation();
        }}
      >
        <div className="space-y-3">
          <div className="space-y-1.5">
            <div className="space-y-2">
              <h4 className="leading-none font-medium">Review Translation</h4>
              <p className="text-muted-foreground text-sm">
                Set the dimensions for the layer.
              </p>
            </div>
            <Textarea
              placeholder="Add a comment..."
              value={comment}
              onChange={(e) => {
                setComment(e.target.value);
              }}
              disabled={isSaving}
              rows={2}
              className="text-sm"
              onClick={(e) => {
                e.stopPropagation();
              }}
            />
          </div>

          <div className="space-y-1">
            <Button
              onClick={(e) => {
                e.stopPropagation();
                handleApprove();
              }}
              disabled={isSaving || reviewStatus === "APPROVED"}
              variant="ghost"
              size="sm"
              className="w-full justify-start text-green-600 hover:text-green-700 hover:bg-green-50"
            >
              <Check className="h-4 w-4 mr-2" />
              Approve
            </Button>

            <Button
              onClick={(e) => {
                e.stopPropagation();
                handleReject();
              }}
              disabled={isSaving || reviewStatus === "REJECTED"}
              variant="ghost"
              size="sm"
              className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <X className="h-4 w-4 mr-2" />
              Reject
            </Button>

            {reviewStatus === "APPROVED" || reviewStatus === "REJECTED" ? (
              <Button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteReview();
                }}
                disabled={isSaving}
                variant="ghost"
                size="sm"
                className="w-full justify-start text-muted-foreground hover:text-foreground"
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Cancel Review
              </Button>
            ) : null}
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};
