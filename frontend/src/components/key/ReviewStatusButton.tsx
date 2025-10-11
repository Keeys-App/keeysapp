import { type FC, useState } from "react";
import { useMutation } from "@apollo/client";
import {
  APPROVE_TRANSLATION,
  REJECT_TRANSLATION,
  DELETE_TRANSLATION_REVIEW,
  GET_KEY_LOGS,
  GET_PROJECT_KEYS,
} from "@/graphql/keys";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useSaving, useSavingStore } from "@/stores";
import { toast } from "sonner";
import type { ReviewStatus } from "@/types/translationKey";
  import {
    MessageSquareOff,
    MessageSquareHeart,
    MessageSquare,
    MessageSquareX,
  } from "lucide-react";

interface ReviewStatusButtonProps {
  keyId: string;
  language: string;
  reviewStatus: ReviewStatus;
  projectId: string;
}

const reviewStatusConfig: Record<
  ReviewStatus,
  { icon: typeof MessageSquare; color: string }
> = {
  NOT_REVIEWED: { icon: MessageSquare, color: "text-muted-foreground" },
  PENDING: { icon: MessageSquare, color: "text-muted-foreground" },
  APPROVED: { icon: MessageSquareHeart, color: "text-green-600" },
  REJECTED: { icon: MessageSquareX, color: "text-red-600" },
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

  const StatusIcon = reviewStatusConfig[reviewStatus]?.icon || MessageSquare;
  const statusColor =
    reviewStatusConfig[reviewStatus]?.color || "text-muted-foreground";

  // Review mutations
  const [approveTranslation] = useMutation(APPROVE_TRANSLATION, {
    refetchQueries: [
      {
        query: GET_KEY_LOGS,
        variables: { keyId, limit: 50 },
      },
      {
        query: GET_PROJECT_KEYS,
        variables: { projectId },
      },
    ],
    awaitRefetchQueries: true,
    update(cache) {
      // Invalidate key logs cache to force refetch
      cache.evict({ 
        id: 'ROOT_QUERY',
        fieldName: 'keyLogs',
        args: { keyId },
      });
      cache.gc();
    },
  });

  const [rejectTranslation] = useMutation(REJECT_TRANSLATION, {
    refetchQueries: [
      {
        query: GET_KEY_LOGS,
        variables: { keyId, limit: 50 },
      },
      {
        query: GET_PROJECT_KEYS,
        variables: { projectId },
      },
    ],
    awaitRefetchQueries: true,
    update(cache) {
      // Invalidate key logs cache to force refetch
      cache.evict({ 
        id: 'ROOT_QUERY',
        fieldName: 'keyLogs',
        args: { keyId },
      });
      cache.gc();
    },
  });

  const [deleteTranslationReview] = useMutation(DELETE_TRANSLATION_REVIEW, {
    refetchQueries: [
      {
        query: GET_KEY_LOGS,
        variables: { keyId, limit: 50 },
      },
      {
        query: GET_PROJECT_KEYS,
        variables: { projectId },
      },
    ],
    awaitRefetchQueries: true,
    update(cache) {
      // Invalidate key logs cache to force refetch
      cache.evict({ 
        id: 'ROOT_QUERY',
        fieldName: 'keyLogs',
        args: { keyId },
      });
      cache.gc();
    },
  });

  const handleApprove = async () => {
    await withSaving(async () => {
      const result = await approveTranslation({
        variables: {
          input: {
            keyId,
            language,
            comment: comment.trim() || null,
          },
        },
      });

      if (result.data?.approveTranslation) {
        setComment("");
        setIsOpen(false);
        toast("Translation approved");
      }
    }, "Approving...");
  };

  const handleReject = async () => {
    await withSaving(async () => {
      const result = await rejectTranslation({
        variables: {
          input: {
            keyId,
            language,
            comment: comment.trim() || null,
          },
        },
      });

      if (result.data?.rejectTranslation) {
        setComment("");
        setIsOpen(false);
        toast("Translation rejected");
      }
    }, "Rejecting...");
  };

  const handleDeleteReview = async () => {
    await withSaving(async () => {
      const result = await deleteTranslationReview({
        variables: {
          keyId,
          language,
        },
      });

      if (result.data?.deleteTranslationReview) {
        setIsOpen(false);
        toast("Review reset");
      }
    }, "Revoking...");
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
                Review the translation and approve or reject it.
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
            <div className="grid grid-cols-2 gap-2">
               {reviewStatus !== "APPROVED" && 
               <Button
                 onClick={(e) => {
                   e.stopPropagation();
                   handleApprove();
                 }}
                 disabled={isSaving}
                 variant="ghost"
                 size="sm"
                 className="justify-start text-green-600 hover:text-green-700 hover:bg-green-50"
               >
                 <MessageSquareHeart className="h-4 w-4 mr-2" />
                 Approve
               </Button>
               }

              {reviewStatus !== "REJECTED" && <Button
                onClick={(e) => {
                  e.stopPropagation();
                  handleReject();
                }}
                disabled={isSaving}
                variant="ghost"
                size="sm"
                className="justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                <MessageSquareX className="h-4 w-4 mr-2" />
                Reject
              </Button>}

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
                   <MessageSquareOff className="h-4 w-4 mr-2" />
                   Revoke
                 </Button>
               ) : null}
            </div>
          </div>
        </div>
      </PopoverContent>
    </Popover>
  );
};
