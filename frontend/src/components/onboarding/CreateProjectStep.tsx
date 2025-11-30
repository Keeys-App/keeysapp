import { useState, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useSaving, useSavingStore } from '@/stores';
import { toast } from 'sonner';
import {
  CREATE_PROJECT,
  GET_PROJECTS,
  type CreateProjectInput,
  type LanguageConfigInput,
} from '@/graphql/projects';
import { DEFAULT_PROJECT_COLORS, ProjectStatus } from '@/types/project';
import { ColorPicker } from '@/components/blocks';
import { LanguageConfigEditor } from '@/components/project/LanguageConfigEditor';

interface CreateProjectStepProps {
  teamId: string;
  onComplete: () => void;
}

export const CreateProjectStep: FC<CreateProjectStepProps> = ({
  teamId,
  onComplete,
}) => {
  const navigate = useNavigate();
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  // Initialize with English language by default
  const [languages, setLanguages] = useState<LanguageConfigInput[]>([
    { code: 'en', locale: 'en-US', direction: 'ltr' },
  ]);
  // Set English as default language
  const [defaultLanguage, setDefaultLanguage] = useState<string>('en');
  const [color, setColor] = useState(DEFAULT_PROJECT_COLORS[0]);

  const [createProject] = useMutation(CREATE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      toast('Project name is required');
      return;
    }

    // Languages and default language are pre-populated with English
    // but we still validate them in case user removed the default
    if (languages.length === 0) {
      toast('At least one language is required');
      return;
    }

    if (!defaultLanguage) {
      toast('Default language is required');
      return;
    }

    await withSaving(
      async () => {
        try {
          const input: CreateProjectInput = {
            name: name.trim(),
            description: description.trim() || undefined,
            languages,
            defaultLanguage: defaultLanguage || undefined,
            color,
            status: ProjectStatus.ACTIVE,
            teamId,
          };

          const result = await createProject({ variables: { input } });

          if (result.data?.createProject) {
            toast('Project created successfully');
            onComplete();
            navigate(`/project/${result.data.createProject.id}`);
          }
        } catch (error: any) {
          toast('Failed to create project. Please try again.');
        }
      },
      'Creating project...'
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="name">Project Name *</Label>
          <Input
            id="name"
            value={name}
            onChange={(e) => {
              return setName(e.target.value);
            }}
            placeholder="My First Project"
            required
            disabled={isSaving}
            autoFocus
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="description">Description</Label>
          <Textarea
            id="description"
            value={description}
            onChange={(e) => {
              return setDescription(e.target.value);
            }}
            placeholder="Brief description of your project..."
            rows={3}
            disabled={isSaving}
          />
        </div>

        <div className="space-y-2">
          <Label>Color</Label>
          <ColorPicker
            value={color}
            onChange={setColor}
            colors={DEFAULT_PROJECT_COLORS}
            disabled={isSaving}
          />
        </div>

        <div className="space-y-2">
          <Label>Languages *</Label>
          <LanguageConfigEditor
            languages={languages}
            defaultLanguage={defaultLanguage}
            onChange={setLanguages}
            onDefaultLanguageChange={setDefaultLanguage}
            disabled={isSaving}
          />
        </div>
      </div>

      <div className="flex justify-end">
        <Button type="submit" disabled={isSaving}>
          Create Project & Finish
        </Button>
      </div>
    </form>
  );
};

