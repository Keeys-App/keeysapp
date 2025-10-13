import { Search } from "lucide-react";
import { InputGroup, InputGroupAddon, InputGroupButton, InputGroupInput } from "../ui/input-group";

export const KeysSearch = () => {
  return (
    <InputGroup className="bg-background rounded-4xl py-2 w-70">
      <InputGroupAddon>
        <InputGroupButton variant="secondary" size="icon-xs" className="rounded-4xl">
          <Search />
        </InputGroupButton>
      </InputGroupAddon>
      <InputGroupInput type="text" placeholder="Search keys" />
      <InputGroupAddon align="inline-end">12 results</InputGroupAddon>
    </InputGroup>
  );
};
