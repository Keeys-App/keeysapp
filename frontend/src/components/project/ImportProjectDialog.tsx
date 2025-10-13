import { useState, type FC } from "react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useSaving, useSavingStore, useTeamStore } from "@/stores";

interface ImportProjectDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onImportSuccess: () => void;
}

export const ImportProjectDialog: FC<ImportProjectDialogProps> = ({
  open,
  onOpenChange,
  onImportSuccess,
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const withSaving = useSaving();
  const { isSaving } = useSavingStore();
  const { selectedTeamId } = useTeamStore();

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      if (!selectedFile.name.endsWith(".json")) {
        setError("Please select a JSON file");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleImport = async () => {
    if (!file) {
      setError("Please select a file");
      return;
    }

    if (!selectedTeamId) {
      setError("Please select a team from the header");
      toast("Please select a team before importing");
      return;
    }

    setError(null);

    await withSaving(
      async () => {
        try {
          const token = localStorage.getItem("authToken");
          if (!token) {
            throw new Error("Authentication required");
          }

          const formData = new FormData();
          formData.append("file", file);
          formData.append("team_id", selectedTeamId);

          const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
          const response = await fetch(`${API_BASE_URL}/api/projects/import`, {
            method: "POST",
            headers: {
              Authorization: `Bearer ${token}`,
            },
            body: formData,
          });

          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Failed to import project");
          }

          const result = await response.json();

          toast(`Project "${result.name}" imported successfully`);

          // Reset form
          setFile(null);
          setError(null);
          onOpenChange(false);
          onImportSuccess();
        } catch (err) {
          const errorMessage = err instanceof Error ? err.message : "Failed to import project";
          setError(errorMessage);
          toast(errorMessage);
        }
      },
      "Importing project..."
    );
  };

  const handleClose = () => {
    if (!isSaving) {
      setFile(null);
      setError(null);
      onOpenChange(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Import Project</DialogTitle>
          <DialogDescription>
            Upload a JSON file to import a project with all its keys and translations.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="file">Project JSON File</Label>
            <Input
              id="file"
              type="file"
              accept=".json"
              onChange={handleFileChange}
              disabled={isSaving}
            />
            {file ? (
              <p className="text-sm text-muted-foreground">
                Selected: {file.name}
              </p>
            ) : null}
          </div>

          {error ? (
            <Alert variant="destructive">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          ) : null}
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleClose}
            disabled={isSaving}
          >
            Cancel
          </Button>
          <Button
            type="button"
            onClick={handleImport}
            disabled={!file || isSaving}
          >
            Import
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

