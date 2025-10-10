import type { FC, ReactNode } from "react";
import { ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";

interface NotFoundStateProps {
  message: string;
  onBack?: () => void;
  backLabel?: string;
  className?: string;
  children?: ReactNode;
}

export const NotFoundState: FC<NotFoundStateProps> = ({ 
  message,
  onBack,
  backLabel = "Back",
  className = "min-h-[50vh]",
  children
}) => {
  return (
    <div className={`flex flex-col items-center justify-center gap-4 ${className}`}>
      <p className="text-lg text-muted-foreground">{message}</p>
      {children}
      {onBack ? (
        <Button onClick={onBack}>
          <ArrowLeft className="h-4 w-4" /> {backLabel}
        </Button>
      ) : null}
    </div>
  );
};

