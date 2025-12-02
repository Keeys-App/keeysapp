import type { FC } from 'react';
import { Outlet } from 'react-router-dom';
import { Sun, Moon, Languages } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { Button } from '@/components/ui/button';

export const AuthLayout: FC = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="bg-muted flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="absolute top-5 right-5">
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
        >
          {theme === 'light' ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </Button>
      </div>

      <div className="flex w-full max-w-sm flex-col gap-6">
        <a
          href="/"
          className="flex items-center gap-2 self-center font-medium"
        >
          <div className="bg-primary text-primary-foreground flex size-6 items-center justify-center rounded-md">
            <Languages className="size-4" />
          </div>
          Keeys
        </a>
        <Outlet />
      </div>
    </div>
  );
};

