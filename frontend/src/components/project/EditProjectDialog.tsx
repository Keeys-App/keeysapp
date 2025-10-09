import { useState, useEffect, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { X } from 'lucide-react';
import { UPDATE_PROJECT, GET_PROJECTS, type UpdateProjectInput, type Project } from '@/graphql/projects';
import { DEFAULT_PROJECT_COLORS, COMMON_LANGUAGES, ProjectStatus } from '@/types/project';
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
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface EditProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  project: Project | null;
}

export const EditProjectDialog: FC<EditProjectDialogProps> = ({ open, onOpenChange, project }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [languages, setLanguages] = useState<string[]>([]);
  const [color, setColor] = useState(DEFAULT_PROJECT_COLORS[0]);
  const [status, setStatus] = useState<string>(ProjectStatus.ACTIVE);
  const [languageInput, setLanguageInput] = useState('');

  // Initialize form with project data
  useEffect(() => {
    if (project) {
      setName(project.name);
      setDescription(project.description || '');
      setLanguages(project.languages || []);
      setColor(project.color);
      setStatus(project.status);
    }
  }, [project]);

  const [updateProject, { loading }] = useMutation(UPDATE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
    onCompleted: () => {
      onOpenChange(false);
    },
    onError: (error) => {
      console.error('Error updating project:', error);
      alert('Failed to update project. Please try again.');
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!project || !name.trim()) {
      return;
    }

    const input: UpdateProjectInput = {
      id: project.id,
      name: name.trim(),
      description: description.trim() || null,
      languages,
      color,
      status: status as 'active' | 'archived' | 'draft',
    };

    await updateProject({ variables: { input } });
  };

  const handleAddLanguage = (langCode: string) => {
    if (langCode && !languages.includes(langCode)) {
      setLanguages([...languages, langCode]);
    }
  };

  const handleRemoveLanguage = (langCode: string) => {
    setLanguages(
      languages.filter((l) => {
        return l !== langCode;
      })
    );
  };

  const handleAddCustomLanguage = () => {
    const trimmed = languageInput.trim().toLowerCase();
    if (trimmed && !languages.includes(trimmed)) {
      setLanguages([...languages, trimmed]);
      setLanguageInput('');
    }
  };

  if (!project) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Edit Project</DialogTitle>
          <DialogDescription>Update your project settings.</DialogDescription>
        </DialogHeader>

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
            <FieldLabel>Languages</FieldLabel>

            {/* Selected languages */}
            {languages.length > 0 ? (
              <div className="flex gap-2 flex-wrap mb-2">
                {languages.map((lang) => {
                  return (
                    <Badge
                      key={lang}
                      variant="secondary"
                      className="cursor-pointer"
                      onClick={() => {
                        return handleRemoveLanguage(lang);
                      }}
                    >
                      {lang.toUpperCase()} <X className="h-3 w-3 ml-1" />
                    </Badge>
                  );
                })}
              </div>
            ) : null}

            {/* Language selector */}
            <Select value="" onValueChange={handleAddLanguage} disabled={loading}>
              <SelectTrigger>
                <SelectValue placeholder="Select languages..." />
              </SelectTrigger>
              <SelectContent>
                {COMMON_LANGUAGES.map((lang) => {
                  return (
                    <SelectItem key={lang.code} value={lang.code}>
                      {lang.name} ({lang.code})
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>

            {/* Custom language input */}
            <div className="flex gap-2 mt-2">
              <Input
                placeholder="Or add custom code (e.g., en-US)"
                value={languageInput}
                onChange={(e) => {
                  return setLanguageInput(e.target.value);
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    handleAddCustomLanguage();
                  }
                }}
                disabled={loading}
                className="flex-1"
              />
              <Button
                type="button"
                variant="secondary"
                onClick={handleAddCustomLanguage}
                disabled={loading || !languageInput.trim()}
              >
                Add
              </Button>
            </div>
          </Field>

          {/* Color */}
          <Field>
            <FieldLabel>Color</FieldLabel>
            <div className="flex gap-2 flex-wrap">
              {DEFAULT_PROJECT_COLORS.map((c) => {
                return (
                  <button
                    key={c}
                    type="button"
                    onClick={() => {
                      return setColor(c);
                    }}
                    className="w-8 h-8 rounded-md transition-all"
                    style={{
                      backgroundColor: c,
                      border: color === c ? '3px solid hsl(var(--primary))' : '2px solid hsl(var(--border))',
                    }}
                  />
                );
              })}
            </div>
          </Field>

          {/* Status */}
          <Field>
            <FieldLabel>Status</FieldLabel>
            <Select value={status} onValueChange={setStatus} disabled={loading}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={ProjectStatus.ACTIVE}>Active</SelectItem>
                <SelectItem value={ProjectStatus.DRAFT}>Draft</SelectItem>
                <SelectItem value={ProjectStatus.ARCHIVED}>Archived</SelectItem>
              </SelectContent>
            </Select>
          </Field>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
