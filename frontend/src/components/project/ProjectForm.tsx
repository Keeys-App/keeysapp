import { useState, useEffect, type FC } from "react";
import { useMutation } from "@apollo/client";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { ArrowLeft } from "lucide-react";
import { useSaving, useSavingStore } from "@/stores";
import {
  CREATE_PROJECT,
  UPDATE_PROJECT,
  GET_PROJECTS,
  type CreateProjectInput,
  type UpdateProjectInput,
  type Project,
  type LanguageConfigInput,
} from "@/graphql/projects";
import {
  DEFAULT_PROJECT_COLORS,
  ProjectStatus,
} from "@/types/project";
import { useAuth } from "@/contexts/AuthContext";
import { ColorPicker } from "@/components/blocks";
import { getUserFriendlyErrorMessage } from "@/lib/utils";
import { Input } from "@/components/ui/input";
import { Field, FieldLabel } from "@/components/ui/field";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { LanguageConfigEditor } from "./LanguageConfigEditor";
import { useTeamStore } from "@/stores";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertCircle } from "lucide-react";

interface ProjectFormProps {
  mode: "create" | "edit";
  project?: Project | null;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export const ProjectForm: FC<ProjectFormProps> = ({
  mode,
  project,
  onSuccess,
  onCancel,
}) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [languages, setLanguages] = useState<LanguageConfigInput[]>([]);
  const [defaultLanguage, setDefaultLanguage] = useState<string>("");
  const [color, setColor] = useState(DEFAULT_PROJECT_COLORS[0]);
  const [status, setStatus] = useState<string>(ProjectStatus.ACTIVE);
  
  const { selectedTeamId } = useTeamStore();

  // Store original values for edit mode
  const [originalValues, setOriginalValues] = useState<{
    name: string;
    description: string;
    languages: LanguageConfigInput[];
    defaultLanguage: string;
    color: string;
    status: string;
  } | null>(null);

  const navigate = useNavigate();
  const { logout } = useAuth();

  // Initialize form with project data in edit mode
  useEffect(() => {
    if (mode === "edit" && project) {
      setName(project.name);
      setDescription(project.description || "");

      // Languages are always in the correct format: {code: string, locale: string, direction: string}
      const languages = (project.languages || []).map(
        (lang): LanguageConfigInput => ({
          code: lang.code,
          locale: lang.locale,
          direction: lang.direction,
        })
      );

      setLanguages(languages);
      // Use actual value from project, including null/undefined - convert to empty string only if truly empty
      const defaultLang = project.defaultLanguage ?? "";
      setDefaultLanguage(defaultLang);
      setColor(project.color);
      setStatus(project.status);

      // Store original values for comparison
      setOriginalValues({
        name: project.name,
        description: project.description || "",
        languages: languages,
        defaultLanguage: defaultLang,
        color: project.color,
        status: project.status,
      });
    }
  }, [mode, project]);

  const [
    createProject,
    { data: createData, error: createError },
  ] = useMutation(CREATE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
  });

  const [
    updateProject,
    { data: updateData, error: updateError },
  ] = useMutation(UPDATE_PROJECT, {
    refetchQueries: [{ query: GET_PROJECTS }],
  });

  const withSaving = useSaving();
  const { isSaving } = useSavingStore();

  // Handle create project success
  useEffect(() => {
    if (createData) {
      toast("Project created successfully");
      if (onSuccess) {
        onSuccess();
      } else {
        // Redirect to the created project page
        navigate(`/project/${createData.createProject.id}`);
      }
    }
  }, [createData, onSuccess, navigate]);

  // Handle create project error
  useEffect(() => {
    if (createError) {
      // Check if it's an authentication error
      if (createError.message.includes("Authentication required")) {
        logout();
        navigate("/auth");
        return;
      }

      const message = getUserFriendlyErrorMessage(
        createError,
        "Failed to create project. Please try again."
      );
      toast(message);
    }
  }, [createError, logout, navigate]);

  // Handle update project success
  useEffect(() => {
    if (updateData) {
      toast("Project updated successfully");
      if (onSuccess) {
        onSuccess();
      }
    }
  }, [updateData, onSuccess]);

  // Handle update project error
  useEffect(() => {
    if (updateError) {
      const message = getUserFriendlyErrorMessage(
        updateError,
        "Failed to update project. Please try again."
      );
      toast(message);
    }
  }, [updateError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      toast("Please enter a project name");
      return;
    }

    if (mode === "create" && !selectedTeamId) {
      toast("Please select a team from the header");
      return;
    }

    if (!defaultLanguage) {
      toast("Please select a default language");
      return;
    }

    // Clean languages data - remove __typename if present
    const cleanLanguages = languages.map((lang) => {
      return {
        code: lang.code,
        locale: lang.locale,
        direction: lang.direction,
      };
    });

    if (mode === "create") {
      const input: CreateProjectInput = {
        name: name.trim(),
        teamId: selectedTeamId!,
        description: description.trim() || null,
        languages: cleanLanguages,
        defaultLanguage,
        color,
        status: status as "active" | "archived" | "draft",
      };

      await withSaving(
        async () => {
          await createProject({ variables: { input } });
        },
        "Creating project..."
      );
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
        status: status as "active" | "archived" | "draft",
      };

      await withSaving(
        async () => {
          await updateProject({ variables: { input } });
        },
        "Updating project..."
      );
    }
  };

  // Check if form has changes (for edit mode)
  const hasChanges = (): boolean => {
    if (mode === "create" || !originalValues) {
      return true;
    }

    // Compare primitive values
    if (
      name !== originalValues.name ||
      description !== originalValues.description ||
      defaultLanguage !== originalValues.defaultLanguage ||
      color !== originalValues.color ||
      status !== originalValues.status
    ) {
      return true;
    }

    // Compare languages arrays
    if (languages.length !== originalValues.languages.length) {
      return true;
    }

    // Deep compare languages (order-independent)
    // Sort both arrays by code for consistent comparison
    const sortedLanguages = [...languages].sort((a, b) => {
      return a.code.localeCompare(b.code);
    });
    const sortedOriginalLanguages = [...originalValues.languages].sort(
      (a, b) => {
        return a.code.localeCompare(b.code);
      }
    );

    const languagesChanged = sortedLanguages.some((lang, index) => {
      const originalLang = sortedOriginalLanguages[index];
      return (
        lang.code !== originalLang?.code || lang.locale !== originalLang?.locale
      );
    });

    return languagesChanged;
  };

  const handleLanguagesChange = (newLanguages: LanguageConfigInput[]) => {
    setLanguages(newLanguages);

    // Auto-select as default if it's the first language
    if (newLanguages.length === 1 && !defaultLanguage) {
      setDefaultLanguage(newLanguages[0].code);
    }

    // Clear default language if it was removed
    if (
      defaultLanguage &&
      !newLanguages.some((l) => {
        return l.code === defaultLanguage;
      })
    ) {
      setDefaultLanguage(newLanguages.length > 0 ? newLanguages[0].code : "");
    }
  };

  const handleDefaultLanguageChange = (langCode: string) => {
    setDefaultLanguage(langCode);
  };

  const handleCancel = () => {
    if (onCancel) {
      onCancel();
    } else {
      navigate("/");
    }
  };

  return (
    <div className="container max-w-2xl py-8">
      <Card>
        <CardHeader>
          <CardTitle>
            {mode === "create" ? "Create New Project" : "Edit Project"}
          </CardTitle>
          <CardDescription>
            {mode === "create"
              ? "Create a new localization project to manage your translations."
              : "Update your project settings."}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            key={mode === "edit" && project ? project.id : "create"}
            onSubmit={handleSubmit}
            className="space-y-4"
          >
            {/* Team Info - show which team the project will be created in */}
            {mode === "create" && selectedTeamId ? (
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Creating in team</AlertTitle>
                <AlertDescription>
                  This project will be created in the currently selected team.
                  You can change the team using the selector in the header.
                </AlertDescription>
              </Alert>
            ) : null}
            
            {/* Team Warning - only in create mode if no team selected */}
            {mode === "create" && !selectedTeamId ? (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>No team selected</AlertTitle>
                <AlertDescription>
                  Please select a team from the header before creating a project.
                  A team should be automatically selected if you have any.
                </AlertDescription>
              </Alert>
            ) : null}

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
                disabled={isSaving}
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
                disabled={isSaving}
                rows={3}
              />
            </Field>

            {/* Languages */}
            <Field>
              <FieldLabel>
                Languages <span className="text-destructive">*</span>
              </FieldLabel>
              <p className="text-sm text-muted-foreground mb-2">
                Add languages and select default language using radio buttons
              </p>
              <LanguageConfigEditor
                languages={languages}
                onChange={handleLanguagesChange}
                defaultLanguage={defaultLanguage}
                onDefaultLanguageChange={handleDefaultLanguageChange}
                disabled={isSaving}
              />
            </Field>

            {/* Color */}
            <Field>
              <FieldLabel>Color</FieldLabel>
              <ColorPicker
                value={color}
                onChange={setColor}
                disabled={isSaving}
              />
            </Field>

            {/* Status */}
            <Field>
              <FieldLabel>Status</FieldLabel>
              <Select
                value={status}
                onValueChange={setStatus}
                disabled={isSaving}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ProjectStatus.ACTIVE}>Active</SelectItem>
                  <SelectItem value={ProjectStatus.DRAFT}>Draft</SelectItem>
                  <SelectItem value={ProjectStatus.ARCHIVED}>
                    Archived
                  </SelectItem>
                </SelectContent>
              </Select>
            </Field>

            <div className="flex gap-2 justify-end pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={handleCancel}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={
                  isSaving || !name.trim() || !defaultLanguage || !hasChanges()
                }
              >
                {mode === "create" ? "Create Project" : "Save Changes"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};
