import { useState } from 'react';
import { useMutation } from '@apollo/client';
import { SET_TRANSLATION, GET_PROJECT_KEYS } from '@/graphql/keys';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface TranslationEditorProps {
  keyId: string;
  language: string;
  currentValue: string;
  projectId: string;
}

export function TranslationEditor({ keyId, language, currentValue, projectId }: TranslationEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [value, setValue] = useState(currentValue);

  const [setTranslation, { loading }] = useMutation(SET_TRANSLATION, {
    refetchQueries: [{ query: GET_PROJECT_KEYS, variables: { projectId } }],
    onCompleted: () => {
      setIsEditing(false);
    },
    onError: (error) => {
      alert(`Error: ${error.message}`);
    },
  });

  const handleSave = async () => {
    const trimmedValue = value.trim();
    
    // Allow empty value to delete translation
    await setTranslation({
      variables: {
        input: {
          keyId,
          language,
          value: trimmedValue,
        },
      },
    });
  };

  const handleCancel = () => {
    setValue(currentValue);
    setIsEditing(false);
  };

  if (!isEditing) {
    return (
      <div className="flex gap-4 items-start group">
        <span className="font-medium text-sm w-12 shrink-0">
          {language}
        </span>
        <span className="text-sm flex-1">
          {currentValue || <span className="text-muted-foreground italic">No translation</span>}
        </span>
        <Button
          variant="ghost"
          size="sm"
          className="opacity-0 group-hover:opacity-100 transition-opacity"
          onClick={() => setIsEditing(true)}
        >
          {currentValue ? 'Edit' : 'Add'}
        </Button>
      </div>
    );
  }

  return (
    <div className="flex gap-2 items-center">
      <span className="font-medium text-sm w-12 shrink-0">
        {language}
      </span>
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        disabled={loading}
        className="flex-1"
      />
      <Button
        size="sm"
        onClick={handleSave}
        disabled={loading}
      >
        Save
      </Button>
      <Button
        size="sm"
        variant="outline"
        onClick={handleCancel}
        disabled={loading}
      >
        Cancel
      </Button>
    </div>
  );
}

