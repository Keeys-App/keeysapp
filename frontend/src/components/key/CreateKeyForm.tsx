import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { CREATE_KEY, GET_PROJECT_KEYS } from '@/graphql/keys';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface CreateKeyFormProps {
  projectId: string;
}

export function CreateKeyForm({ projectId }: CreateKeyFormProps) {
  const [key, setKey] = useState('');
  const [description, setDescription] = useState('');

  const [createKey, { loading }] = useMutation(CREATE_KEY, {
    refetchQueries: [{ query: GET_PROJECT_KEYS, variables: { projectId } }],
    onCompleted: () => {
      setKey('');
      setDescription('');
    },
    onError: (error) => {
      alert(`Error: ${error.message}`);
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!key.trim()) {
      alert('Please enter a key');
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
    <Card>
      <CardHeader>
        <CardTitle>Add New Key</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-3">
          <div>
            <Input
              placeholder="Key (e.g., button.submit)"
              value={key}
              onChange={(e) => setKey(e.target.value)}
              disabled={loading}
            />
          </div>
          <div>
            <Input
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={loading}
            />
          </div>
          <Button type="submit" disabled={loading}>
            {loading ? 'Creating...' : 'Create Key'}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}

