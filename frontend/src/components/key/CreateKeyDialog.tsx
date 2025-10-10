import { useState, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { toast } from 'sonner';
import { CREATE_KEY, GET_PROJECT_KEYS } from '@/graphql/keys';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Field, FieldLabel } from '@/components/ui/field';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';

interface CreateKeyDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  projectId: string;
}

export const CreateKeyDialog: FC<CreateKeyDialogProps> = ({ open, onOpenChange, projectId }) => {
  const [key, setKey] = useState('');
  const [description, setDescription] = useState('');

  const [createKey, { loading }] = useMutation(CREATE_KEY, {
    refetchQueries: [{ query: GET_PROJECT_KEYS, variables: { projectId } }],
    onCompleted: () => {
      // Reset form
      setKey('');
      setDescription('');
      onOpenChange(false);
      toast.success('Key created successfully');
    },
    onError: (error) => {
      console.error('Error creating key:', error);
      toast.error(`Failed to create key: ${error.message}`);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!key.trim()) {
      toast.error('Please enter a key');
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
          <Field>
            <FieldLabel>
              Key <span className="text-destructive">*</span>
            </FieldLabel>
            <Input
              placeholder="button.submit"
              value={key}
              onChange={(e) => {
                return setKey(e.target.value);
              }}
              disabled={loading}
              required
            />
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

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Key'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

