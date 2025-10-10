import { useState } from "react";
import { useMutation } from "@apollo/client";
import { toast } from "sonner";
import { SET_TRANSLATION, GET_PROJECT_KEYS } from "@/graphql/keys";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";

interface TranslationEditorProps {
  keyId: string;
  language: string;
  currentValue: string;
  projectId: string;
}

export function TranslationEditor({
  keyId,
  language,
  currentValue,
  projectId,
}: TranslationEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [value, setValue] = useState(currentValue);

  const [setTranslation, { loading }] = useMutation(SET_TRANSLATION, {
    refetchQueries: [{ query: GET_PROJECT_KEYS, variables: { projectId } }],
    onCompleted: () => {
      setIsEditing(false);
      toast("Translation updated successfully");
    },
    onError: (error) => {
      toast(`Error: ${error.message}`);
    },
  });

  const handleSave = async () => {
    const trimmedValue = value.trim();

    // Allow empty value to delete translation
    await setTranslation({
      variables: {
        input: {
          keyId,
          value: trimmedValue,
          language,
        },
      },
    });
  };

  const handleCancel = () => {
    setValue(currentValue);
    setIsEditing(false);
  };

  return <div className="">
    <Textarea value={value} onChange={(e) => setValue(e.target.value)} />
    <Button onClick={handleSave}>Save</Button>
  </div>;
}
