import { useState, useEffect, type FC } from 'react';
import {
  Dialog,
  Flex,
  Text,
  TextField,
  TextArea,
  Button,
  Select,
  Badge,
  Box,
} from '@radix-ui/themes';
import { useMutation } from '@apollo/client';
import { useNavigate } from 'react-router-dom';
import { UPDATE_PROJECT, GET_PROJECTS, type UpdateProjectInput, type Project } from '../graphql/projects';
import { DEFAULT_PROJECT_COLORS, COMMON_LANGUAGES, ProjectStatus } from '../types/project';
import { useAuth } from '../contexts/AuthContext';

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
    setLanguages(languages.filter((l) => {
      return l !== langCode;
    }));
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
    <Dialog.Root open={open} onOpenChange={onOpenChange}>
      <Dialog.Content style={{ maxWidth: 500 }}>
        <Dialog.Title>Edit Project</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          Update your project settings.
        </Dialog.Description>

        <form onSubmit={handleSubmit}>
          <Flex direction="column" gap="4">
            {/* Name */}
            <label>
              <Text as="div" size="2" mb="1" weight="medium">
                Name *
              </Text>
              <TextField.Root
                placeholder="My Awesome Project"
                value={name}
                onChange={(e) => {
                  return setName(e.target.value);
                }}
                disabled={loading}
                required
              />
            </label>

            {/* Description */}
            <label>
              <Text as="div" size="2" mb="1" weight="medium">
                Description
              </Text>
              <TextArea
                placeholder="Describe your project..."
                value={description}
                onChange={(e) => {
                  return setDescription(e.target.value);
                }}
                disabled={loading}
                rows={3}
              />
            </label>

            {/* Languages */}
            <Box>
              <Text as="div" size="2" mb="2" weight="medium">
                Languages
              </Text>
              
              {/* Selected languages */}
              {languages.length > 0 ? (
                <Flex gap="2" wrap="wrap" mb="2">
                  {languages.map((lang) => {
                    return (
                      <Badge key={lang} size="2" style={{ cursor: 'pointer' }} onClick={() => {
                        return handleRemoveLanguage(lang);
                      }}>
                        {lang.toUpperCase()} ×
                      </Badge>
                    );
                  })}
                </Flex>
              ) : null}

              {/* Language selector */}
              <Select.Root
                value=""
                onValueChange={handleAddLanguage}
                disabled={loading}
              >
                <Select.Trigger placeholder="Select languages..." />
                <Select.Content>
                  {COMMON_LANGUAGES.map((lang) => {
                    return (
                      <Select.Item key={lang.code} value={lang.code}>
                        {lang.name} ({lang.code})
                      </Select.Item>
                    );
                  })}
                </Select.Content>
              </Select.Root>

              {/* Custom language input */}
              <Flex gap="2" mt="2">
                <TextField.Root
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
                  style={{ flex: 1 }}
                />
                <Button
                  type="button"
                  variant="soft"
                  onClick={handleAddCustomLanguage}
                  disabled={loading || !languageInput.trim()}
                >
                  Add
                </Button>
              </Flex>
            </Box>

            {/* Color */}
            <Box>
              <Text as="div" size="2" mb="2" weight="medium">
                Color
              </Text>
              <Flex gap="2" wrap="wrap">
                {DEFAULT_PROJECT_COLORS.map((c) => {
                  return (
                    <Box
                      key={c}
                      onClick={() => {
                        return setColor(c);
                      }}
                      style={{
                        width: 32,
                        height: 32,
                        backgroundColor: c,
                        borderRadius: 6,
                        cursor: 'pointer',
                        border: color === c ? '3px solid var(--accent-9)' : '2px solid var(--gray-6)',
                        transition: 'all 0.2s',
                      }}
                    />
                  );
                })}
              </Flex>
            </Box>

            {/* Status */}
            <label>
              <Text as="div" size="2" mb="1" weight="medium">
                Status
              </Text>
              <Select.Root value={status} onValueChange={setStatus} disabled={loading}>
                <Select.Trigger />
                <Select.Content>
                  <Select.Item value={ProjectStatus.ACTIVE}>Active</Select.Item>
                  <Select.Item value={ProjectStatus.DRAFT}>Draft</Select.Item>
                  <Select.Item value={ProjectStatus.ARCHIVED}>Archived</Select.Item>
                </Select.Content>
              </Select.Root>
            </label>

            {/* Actions */}
            <Flex gap="3" mt="4" justify="end">
              <Dialog.Close>
                <Button variant="soft" color="gray" type="button" disabled={loading}>
                  Cancel
                </Button>
              </Dialog.Close>
              <Button type="submit" disabled={loading}>
                {loading ? 'Saving...' : 'Save Changes'}
              </Button>
            </Flex>
          </Flex>
        </form>
      </Dialog.Content>
    </Dialog.Root>
  );
};

