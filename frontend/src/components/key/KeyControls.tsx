import type { FC } from "react";
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

interface KeyControlsProps {
  onCreateKey: () => void;
}

export const KeyControls: FC<KeyControlsProps> = ({ onCreateKey }) => {
  return (
    <div className="py-2 px-4 flex gap-2 bg-muted border-b">
      <Menubar>
        <MenubarMenu>
          <MenubarTrigger>Keys</MenubarTrigger>
          <MenubarContent>
            <MenubarItem>
              New Tab <MenubarShortcut>⌘T</MenubarShortcut>
            </MenubarItem>
            <MenubarItem>New Window</MenubarItem>
            <MenubarSeparator />
            <MenubarItem>Share</MenubarItem>
            <MenubarSeparator />
            <MenubarItem>Print</MenubarItem>
          </MenubarContent>
        </MenubarMenu>
      </Menubar>
      <Button onClick={onCreateKey}>
        Add key
      </Button>
    </div>
  );
};
