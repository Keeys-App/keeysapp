import { useState, useEffect, useCallback, type FC } from 'react';
import { useMutation, useLazyQuery } from '@apollo/client';
import { toast } from 'sonner';
import { Info } from 'lucide-react';
import { CREATE_KEY, GET_PROJECT_KEYS, CHECK_KEY_EXISTS } from '@/graphql/keys';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Field, FieldLabel, FieldError } from '@/components/ui/field';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

interface CreateKeyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
}

export const CreateKeyDialog: FC<CreateKeyDialogProps> = ({ open, onOpenChange, projectId }) => {
  const [key, setKey] = useState('');
  const [description, setDescription] = useState('');
  const [addAnother, setAddAnother] = useState(false);
  const [isDuplicate, setIsDuplicate] = useState(false);
  const [lastCheckedKey, setLastCheckedKey] = useState<string>('');

  // Lazy query to check if key exists
  const [checkKeyExists, { loading: checkingKey }] = useLazyQuery(CHECK_KEY_EXISTS, {
    fetchPolicy: 'no-cache', // Don't use cache at all
    onCompleted: (data) => {
      if (data?.checkKeyExists !== undefined) {
        setIsDuplicate(data.checkKeyExists);
        setLastCheckedKey(key.trim()); // Mark this key as checked
      }
    },
    onError: () => {
      setIsDuplicate(false);
      setLastCheckedKey(key.trim()); // Mark as checked even on error
    },
  });

  // Debounced check for key existence
  useEffect(() => {
    const trimmedKey = key.trim();
    
    if (!trimmedKey || !open) {
      setIsDuplicate(false);
      setLastCheckedKey('');
      return;
    }

    // Reset states while waiting for new check
    setIsDuplicate(false);
    setLastCheckedKey(''); // Clear last checked key - new check is starting

    const timeoutId = setTimeout(() => {
      checkKeyExists({
        variables: {
          projectId,
          key: trimmedKey,
        },
      });
    }, 300); // Debounce for 300ms

    return () => {
      return clearTimeout(timeoutId);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, projectId, open]);

  // Reset form when dialog closes
  useEffect(() => {
    if (!open) {
      setKey('');
      setDescription('');
      setIsDuplicate(false);
      setLastCheckedKey('');
    }
  }, [open]);

  // Check if form is valid and ready to submit
  const isFormValid = 
    key.trim() !== '' && 
    !isDuplicate && 
    !checkingKey && 
    key.trim() === lastCheckedKey; // Ensure current key has been checked

  const [createKey, { loading }] = useMutation(CREATE_KEY, {
    refetchQueries: [{ query: GET_PROJECT_KEYS, variables: { projectId } }],
    onCompleted: () => {
      // Reset form
      setKey('');
      setDescription('');
      setIsDuplicate(false);
      setLastCheckedKey(''); // Reset last checked key
      
      // Close dialog only if "Add another key" is not checked
      if (!addAnother) {
        onOpenChange(false);
      }
      
      toast.success('Key created successfully');
    },
    onError: (error) => {
      console.error('Error creating key:', error);
      toast.error(`Failed to create key: ${error.message}`);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Don't submit if still checking or if form is invalid
    if (!isFormValid || checkingKey) {
      return;
    }

    if (!key.trim()) {
      toast.error('Please enter a key');
      return;
    }

    if (isDuplicate) {
      toast.error('This key already exists in the project');
      return;
    }

    await createKey({
      variables: {
        input: {
          projectId,
          key: key.trim(),
          description: description.trim() || undefined,
        },
      },
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Create New Key</DialogTitle>
          <DialogDescription>Add a new translation key to your project.</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Key */}
          <Field data-invalid={isDuplicate || undefined}>
            <FieldLabel>
              Key
            </FieldLabel>
            <Input
              placeholder="button.submit"
              value={key}
              onChange={(e) => {
                return setKey(e.target.value);
              }}
              disabled={loading}
              required
              className={isDuplicate ? 'border-destructive focus-visible:ring-destructive' : ''}
            />
            {isDuplicate ? (
              <FieldError>This key already exists in the project</FieldError>
            ) : null}
          </Field>

          {/* Description */}
          <Field>
            <FieldLabel>Description</FieldLabel>
            <Textarea
              placeholder="Describe the purpose of this key..."
              value={description}
              onChange={(e) => {
                return setDescription(e.target.value);
              }}
              disabled={loading}
              rows={3}
            />
          </Field>

          {/* Add Another Key */}
          <div className="flex items-center gap-2">
            <Checkbox
              id="add-another"
              checked={addAnother}
              onCheckedChange={(checked) => {
                return setAddAnother(checked === true);
              }}
              disabled={loading}
            />
            <label
              htmlFor="add-another"
              className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 cursor-pointer"
            >
              Add another key
            </label>
            <TooltipProvider>
              <Tooltip>
                <TooltipTrigger asChild>
                  <Info className="h-4 w-4 text-muted-foreground cursor-help" />
                </TooltipTrigger>
                <TooltipContent>
                  <p>Keep the dialog open to add multiple keys in a row</p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={!isFormValid || loading}>
              Create Key
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

