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

interface KeyControlsProps {
  projectId: string;
  onCreateKey: () => void;
}

export const KeyControls: FC<KeyControlsProps> = ({
  projectId,
  onCreateKey,
}) => {
  const navigate = useNavigate();

  const handleExportClick = () => {
    navigate(PATHS.EXPORT.replace(":id", projectId));
  };

  const handleImportClick = () => {
    navigate(PATHS.IMPORT.replace(":id", projectId));
  };

  return (
    <div className="py-2 px-4 flex gap-2 bg-muted border-b">
      <Menubar>
        <MenubarMenu>
          <MenubarTrigger>Actions</MenubarTrigger>
          <MenubarContent>
            <MenubarItem onClick={handleImportClick}>Import</MenubarItem>
            <MenubarItem onClick={handleExportClick}>Export</MenubarItem>
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
