import type { FC } from 'react';
import { Outlet } from 'react-router-dom';
import { Sun, Moon, LogOut } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';

export const Layout: FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto p-6">
        <div className="flex flex-col gap-6">
          {/* Header */}
          <header className="flex items-center justify-between w-full">
            <h1 className="text-4xl font-bold">Locales Dashboard</h1>
            <div className="flex gap-3 items-center">
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleTheme}
                aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} theme`}
              >
                {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
              </Button>

              <div className="flex gap-2 items-center">
                <Avatar className="h-8 w-8">
                  <AvatarFallback>{user?.username.charAt(0).toUpperCase() || 'U'}</AvatarFallback>
                </Avatar>
                <span className="text-sm font-medium">{user?.username}</span>
              </div>

              <Button variant="destructive" onClick={handleLogout}>
                <LogOut className="h-4 w-4" />
                Logout
              </Button>
            </div>
          </header>

          {/* Main Content */}
          <main className="mt-8">
            <Outlet />
          </main>
        </div>
      </div>
    </div>
  );
};
