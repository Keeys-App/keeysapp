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
    <div className="py-2 px-4 flex gap-2 bg-muted border-b">
      <Menubar>
        <MenubarMenu>
          <MenubarTrigger>Actions</MenubarTrigger>
          <MenubarContent>
            <MenubarItem onClick={handleImportClick}>Import Keys</MenubarItem>
            <MenubarItem onClick={handleExportClick}>Export Keys</MenubarItem>
            <MenubarSeparator />
            <MenubarItem onClick={handleExportProjectClick}>
              Export Project
            </MenubarItem>
          </MenubarContent>
        </MenubarMenu>
        <MenubarMenu>
          <Link to={PATHS.PROJECT_EDIT.replace(":id", projectId)}>
            <MenubarTrigger>Settings</MenubarTrigger>
          </Link>
        </MenubarMenu>
      </Menubar>
      <Button onClick={onCreateKey}>Add key</Button>
    </div>
  );
};
