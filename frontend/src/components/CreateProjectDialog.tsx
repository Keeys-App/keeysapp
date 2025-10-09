import { useState, type FC } from 'react';
import { useMutation } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { X } from 'lucide-react';
import { CREATE_PROJECT, GET_PROJECTS, type CreateProjectInput } from '../graphql/projects';
import { DEFAULT_PROJECT_COLORS, COMMON_LANGUAGES, ProjectStatus } from '../types/project';
import { useAuth } from '../contexts/AuthContext';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface CreateProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const CreateProjectDialog: FC<CreateProjectDialogProps> = ({ open, onOpenChange }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [languages, setLanguages] = useState<string[]>([]);
  const [color, setColor] = useState(DEFAULT_PROJECT_COLORS[0]);
  const [status, setStatus] = useState<string>(ProjectStatus.ACTIVE);
  const [languageInput, setLanguageInput] = useState('');

  const navigate = useNavigate();
  const { logout } = useAuth();

  const [createProject, { loading }] = useMutation(CREATE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
    onCompleted: () => {
      // Reset form
      setName('');
      setDescription('');
      setLanguages([]);
      setColor(DEFAULT_PROJECT_COLORS[0]);
      setStatus(ProjectStatus.ACTIVE);
      setLanguageInput('');
      onOpenChange(false);
    },
    onError: (error) => {
      console.error('Error creating project:', error);

      // Check if it's an authentication error
      if (error.message.includes('Authentication required')) {
        logout();
        navigate('/auth');
        return;
      }

      alert('Failed to create project. Please try again.');
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      alert('Please enter a project name');
      return;
    }

    const input: CreateProjectInput = {
      name: name.trim(),
      description: description.trim() || null,
      languages,
      color,
      status: status as 'active' | 'archived' | 'draft',
    };

    await createProject({ variables: { input } });
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

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription>Create a new localization project to manage your translations.</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name">
              Name <span className="text-destructive">*</span>
            </Label>
            <Input
              id="name"
              placeholder="My Awesome Project"
              value={name}
              onChange={(e) => {
                return setName(e.target.value);
              }}
              disabled={loading}
              required
            />
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Textarea
              id="description"
              placeholder="Describe your project..."
              value={description}
              onChange={(e) => {
                return setDescription(e.target.value);
              }}
              disabled={loading}
              rows={3}
            />
          </div>

          {/* Languages */}
          <div className="space-y-2">
            <Label>Languages</Label>

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
          </div>

          {/* Color */}
          <div className="space-y-2">
            <Label>Color</Label>
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
          </div>

          {/* Status */}
          <div className="space-y-2">
            <Label>Status</Label>
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
          </div>

          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create Project'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};
