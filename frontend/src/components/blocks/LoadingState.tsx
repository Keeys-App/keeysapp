import type { FC } from "react";

interface LoadingStateProps {
  message?: string;
  className?: string;
}

export const LoadingState: FC<LoadingStateProps> = ({ 
  message = "Loading...",
  className = "min-h-[50vh]"
}) => {
  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      <p className="text-lg text-muted-foreground">{message}</p>
    </div>
  );
};

