import { useEffect } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import { DELETE_KEY, CREATE_KEY, GET_PROJECT_KEYS } from "@/graphql/keys";
import { useSaving, useSavingStore } from "@/stores";
import type { TranslationKey } from "@/types/translationKey";

interface UseKeyActionsOptions {
  keyData?: TranslationKey;
  projectId: string;
  onKeyDeleted?: () => void;
  onDeleteSuccess?: () => void;
}

/**
 * Hook for managing key actions (delete, duplicate)
 * Provides mutations and handlers without UI logic
 */
export function useKeyActions({ 
  keyData, 
  projectId, 
  onKeyDeleted,
  onDeleteSuccess 
}: UseKeyActionsOptions) {
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Delete key mutation
  const [deleteKey, { data: deleteData, error: deleteError, loading: isDeleting }] = useMutation(DELETE_KEY, {
    refetchQueries: [
      {
        query: GET_PROJECT_KEYS,
        variables: { projectId, offset: 0, limit: 20 },
      },
    ],
    awaitRefetchQueries: true,
  });

  // Create key mutation (for duplication)
  const [createKey, { data: createData, error: createError }] = useMutation(CREATE_KEY, {
    refetchQueries: [
      {
        query: GET_PROJECT_KEYS,
        variables: { projectId, offset: 0, limit: 20 },
      },
    ],
    awaitRefetchQueries: true,
  });

  // Handle delete success
  useEffect(() => {
    if (deleteData) {
      toast("Key deleted successfully");
      if (onDeleteSuccess) {
        onDeleteSuccess();
      }
      if (onKeyDeleted) {
        onKeyDeleted();
      }
    }
  }, [deleteData, onKeyDeleted, onDeleteSuccess]);

  // Handle delete error
  useEffect(() => {
    if (deleteError) {
      toast("Failed to delete key");
    }
  }, [deleteError]);

  // Handle duplicate success
  useEffect(() => {
    if (createData) {
      toast("Key duplicated successfully");
    }
  }, [createData]);

  // Handle duplicate error
  useEffect(() => {
    if (createError) {
      toast("Failed to duplicate key");
    }
  }, [createError]);

  /**
   * Delete the key
   */
  const handleDelete = async () => {
    if (!keyData) {
      return;
    }
    
    await withSaving(async () => {
      await deleteKey({
        variables: {
          id: keyData.id,
        },
      });
    }, "Deleting key...");
  };

  /**
   * Duplicate the key with all its translations
   */
  const handleDuplicate = async () => {
    if (!keyData) {
      return;
    }
    
    // Generate unique key name by adding _copy suffix
    let newKeyName = `${keyData.key}_copy`;
    
    // If the key already ends with _copy or _copy_N, increment the counter
    const copyMatch = keyData.key.match(/^(.+)_copy(?:_(\d+))?$/);
    if (copyMatch) {
      const baseName = copyMatch[1];
      const counter = copyMatch[2] ? parseInt(copyMatch[2]) + 1 : 2;
      newKeyName = `${baseName}_copy_${counter}`;
    }

    // Prepare translations object
    const translations: Record<string, string> = {};
    keyData.translations.forEach((translation) => {
      translations[translation.language] = translation.value;
    });

    await withSaving(async () => {
      await createKey({
        variables: {
          input: {
            projectId,
            key: newKeyName,
            description: keyData.description,
            tags: keyData.tags,
            translations,
          },
        },
      });
    }, "Duplicating key...");
  };

  return {
    // State
    isDeleting,
    isSaving,
    
    // Actions
    handleDelete,
    handleDuplicate,
  };
}

