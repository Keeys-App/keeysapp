import { useState, useEffect, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { ArrowLeft } from 'lucide-react';
import {
  CREATE_PROJECT,
  UPDATE_PROJECT,
  GET_PROJECTS,
  type CreateProjectInput,
  type UpdateProjectInput,
  type Project,
  type LanguageConfigInput,
} from '@/graphql/projects';
import { DEFAULT_PROJECT_COLORS, ProjectStatus, LANGUAGE_CONFIGS } from '@/types/project';
import { useAuth } from '@/contexts/AuthContext';
import { ColorPicker } from '@/components/blocks';
import { getUserFriendlyErrorMessage } from '@/lib/utils';
import { Input } from '@/components/ui/input';
import { Field, FieldLabel } from '@/components/ui/field';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LanguageConfigEditor } from './LanguageConfigEditor';

interface ProjectFormProps {
  mode: 'create' | 'edit';
  project?: Project | null;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const ProjectForm: FC<ProjectFormProps> = ({ mode, project, onSuccess, onCancel }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [languages, setLanguages] = useState<LanguageConfigInput[]>([]);
  const [defaultLanguage, setDefaultLanguage] = useState<string>('');
  const [color, setColor] = useState(DEFAULT_PROJECT_COLORS[0]);
  const [status, setStatus] = useState<string>(ProjectStatus.ACTIVE);

  const navigate = useNavigate();
  const { logout } = useAuth();

  // Initialize form with project data in edit mode
  useEffect(() => {
    if (mode === 'edit' && project) {
      setName(project.name);
      setDescription(project.description || '');
      
      // Normalize languages data - ensure it's in the correct format
      const normalizedLanguages = (project.languages || []).map((lang): LanguageConfigInput => {
        // If it's already an object with code and locale, use it
        if (typeof lang === 'object' && lang && 'code' in lang && 'locale' in lang) {
          return {
            code: lang.code,
            locale: lang.locale,
          };
        }
        
        // Fallback: treat as code and apply default locale from LANGUAGE_CONFIGS
        const code = String(lang);
        const langConfig = LANGUAGE_CONFIGS.find((l) => {
          return l.code === code;
        });
        
        return {
          code: code,
          locale: langConfig?.locale || `${code}-${code.toUpperCase()}`,
        };
      });
      
      setLanguages(normalizedLanguages);
      setDefaultLanguage(project.defaultLanguage || '');
      setColor(project.color);
      setStatus(project.status);
    }
  }, [mode, project]);

  const [createProject, { loading: createLoading }] = useMutation(CREATE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
    onCompleted: () => {
      toast.success('Project created successfully');
      if (onSuccess) {
        onSuccess();
      }
    },
    onError: (error) => {
      // Check if it's an authentication error
      if (error.message.includes('Authentication required')) {
        logout();
        navigate('/auth');
        return;
      }

      const message = getUserFriendlyErrorMessage(error, 'Failed to create project. Please try again.');
      toast.error(message);
    },
  });

  const [updateProject, { loading: updateLoading }] = useMutation(UPDATE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
    onCompleted: () => {
      toast.success('Project updated successfully');
      if (onSuccess) {
        onSuccess();
      }
    },
    onError: (error) => {
      const message = getUserFriendlyErrorMessage(error, 'Failed to update project. Please try again.');
      toast.error(message);
    },
  });

  const loading = createLoading || updateLoading;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      toast('Please enter a project name');
      return;
    }

    if (!defaultLanguage) {
      toast('Please select a default language');
      return;
    }

    // Clean languages data - remove __typename if present
    const cleanLanguages = languages.map((lang) => {
      return {
        code: lang.code,
        locale: lang.locale,
      };
    });

    if (mode === 'create') {
      const input: CreateProjectInput = {
        name: name.trim(),
        description: description.trim() || null,
        languages: cleanLanguages,
        defaultLanguage,
        color,
        status: status as 'active' | 'archived' | 'draft',
      };

      await createProject({ variables: { input } });
    } else {
      if (!project) {
        return;
      }

      const input: UpdateProjectInput = {
        id: project.id,
        name: name.trim(),
        description: description.trim() || null,
        languages: cleanLanguages,
        defaultLanguage,
        color,
        status: status as 'active' | 'archived' | 'draft',
      };

      await updateProject({ variables: { input } });
    }
  };

  const handleLanguagesChange = (newLanguages: LanguageConfigInput[]) => {
    setLanguages(newLanguages);
    
    // Auto-select as default if it's the first language
    if (newLanguages.length === 1 && !defaultLanguage) {
      setDefaultLanguage(newLanguages[0].code);
    }
    
    // Clear default language if it was removed
    if (defaultLanguage && !newLanguages.some((l) => {
      return l.code === defaultLanguage;
    })) {
      setDefaultLanguage(newLanguages.length > 0 ? newLanguages[0].code : '');
    }
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      navigate('/');
    }
  };

  return (
    <div className="container max-w-2xl py-8">
      <Card>
        <CardHeader>
          <CardTitle>{mode === 'create' ? 'Create New Project' : 'Edit Project'}</CardTitle>
          <CardDescription>
            {mode === 'create'
              ? 'Create a new localization project to manage your translations.'
              : 'Update your project settings.'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <Field>
              <FieldLabel>
                Name <span className="text-destructive">*</span>
              </FieldLabel>
              <Input
                placeholder="My Awesome Project"
                value={name}
                onChange={(e) => {
                  return setName(e.target.value);
                }}
                disabled={loading}
                required
              />
            </Field>

            {/* Description */}
            <Field>
              <FieldLabel>Description</FieldLabel>
              <Textarea
                placeholder="Describe your project..."
                value={description}
                onChange={(e) => {
                  return setDescription(e.target.value);
                }}
                disabled={loading}
                rows={3}
              />
            </Field>

            {/* Languages */}
            <Field>
              <FieldLabel>
                Languages <span className="text-destructive">*</span>
              </FieldLabel>
              <LanguageConfigEditor
                languages={languages}
                onChange={handleLanguagesChange}
                disabled={loading}
              />
            </Field>

            {/* Default Language */}
            <Field>
              <FieldLabel>
                Default Language <span className="text-destructive">*</span>
              </FieldLabel>
              <Select
                value={defaultLanguage}
                onValueChange={setDefaultLanguage}
                disabled={loading || languages.length === 0}
              >
                <SelectTrigger>
                  <SelectValue
                    placeholder={languages.length === 0 ? 'Add languages first' : 'Select default language'}
                  />
                </SelectTrigger>
                <SelectContent>
                  {languages.map((lang) => {
                    return (
                      <SelectItem key={lang.code} value={lang.code}>
                        {lang.code.toUpperCase()}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            </Field>

            {/* Color */}
            <Field>
              <FieldLabel>Color</FieldLabel>
              <ColorPicker value={color} onChange={setColor} disabled={loading} />
            </Field>

            {/* Status */}
            <Field>
              <FieldLabel>Status</FieldLabel>
              <Select value={status} onValueChange={setStatus} disabled={loading}>
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ProjectStatus.ACTIVE}>Active</SelectItem>
                  <SelectItem value={ProjectStatus.DRAFT}>Draft</SelectItem>
                  <SelectItem value={ProjectStatus.ARCHIVED}>Archived</SelectItem>
                </SelectContent>
              </Select>
            </Field>

            <div className="flex gap-2 justify-end pt-4">
              <Button type="button" variant="outline" onClick={handleCancel} disabled={loading}>
                Cancel
              </Button>
              <Button type="submit" disabled={loading || !name.trim() || !defaultLanguage}>
                {loading
                  ? mode === 'create'
                    ? 'Creating...'
                    : 'Saving...'
                  : mode === 'create'
                    ? 'Create Project'
                    : 'Save Changes'}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

