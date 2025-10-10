import type { FC } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import {
  Menubar,
  MenubarContent,
  MenubarItem,
  MenubarMenu,
  MenubarSeparator,
  MenubarShortcut,
  MenubarTrigger,
} from "../ui/menubar";
import { PATHS } from "@/constants/paths";
import { toast } from "sonner";
import { useSaving } from "@/stores";

interface KeyControlsProps {
  projectId: string;
  onCreateKey: () => void;
}

export const KeyControls: FC<KeyControlsProps> = ({
  projectId,
  onCreateKey,
}) => {
  const navigate = useNavigate();
  const withSaving = useSaving();

  const handleExportClick = () => {
    navigate(PATHS.EXPORT.replace(":id", projectId));
  };

  const handleImportClick = () => {
    navigate(PATHS.IMPORT.replace(":id", projectId));
  };

  const handleExportProjectClick = async () => {
    await withSaving(
      async () => {
        try {
          const token = localStorage.getItem("authToken");
          if (!token) {
            toast("Authentication required");
            return;
          }

          const API_BASE_URL =
            import.meta.env.VITE_API_URL || "http://localhost:8000";
          const response = await fetch(
            `${API_BASE_URL}/api/projects/${projectId}/export`,
            {
              method: "GET",
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (!response.ok) {
            throw new Error("Failed to export project");
          }

          const data = await response.json();
          const blob = new Blob([JSON.stringify(data, null, 2)], {
            type: "application/json",
          });

          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = `${data.name
            .replace(/\s+/g, "_")
            .toLowerCase()}_export.json`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);

          toast("Project exported successfully");
        } catch (error) {
          console.error("Export error:", error);
          toast("Failed to export project");
        }
      },
      "Exporting project..."
    );
  };

  return (
    <div className="h-12 py-1 px-2 flex gap-2 items-center justify-end bg-muted border-b">
      <Button size="sm" onClick={onCreateKey}>Add key</Button>
    </div>
  );
};
