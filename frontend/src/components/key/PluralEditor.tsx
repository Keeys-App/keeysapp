import type { TranslationTextEditorRef } from "./TranslationTextEditor";
import { Fragment, type FC } from "react";
import type { Language, LanguageWithLocale } from "@/types/project";
import { Badge } from "../ui";
import { TranslationEditForm } from "./TranslationEditForm";

interface PluralEditorProps {
  language: Language | LanguageWithLocale;
  value: string;
  direction?: "ltr" | "rtl";
  onChange: (value: string) => void;
  onSave: () => void;
  onCancel: () => void;
  hasChanges: boolean;
  defaultLanguageValue?: string;
  markReviewedOnSave?: boolean;
  onMarkReviewedOnSaveChange?: (value: boolean) => void;
  onEditorReady?: (ref: TranslationTextEditorRef | null) => void;
}

export const PluralEditor: FC<PluralEditorProps> = (props) => {
  return (
    <div className="grid grid-cols-[auto_1fr] -mb-[1px]">
      {props.language.pluralForms.map((form) => {
        return (
          <Fragment key={form}>
            <div className="capitalize text-muted-foreground border-b p-2 border-r">
              <Badge className="capitalize">{form}</Badge>
            </div>
            <div className="border-b p-2">
              Editor will be here
            </div>
          </Fragment>
        );
      })}
    </div>
  );
};
