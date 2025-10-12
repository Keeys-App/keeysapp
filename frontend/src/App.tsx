import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, TranslationEditorProvider } from '@/contexts';
import { ProtectedRoute, Layout, AuthLayout } from '@/components/layout';
import { AuthPage } from '@/pages/AuthPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { TeamsPage } from '@/pages/TeamsPage';
import { CreateTeamPage } from '@/pages/CreateTeamPage';
import { ProjectPage } from '@/pages/ProjectPage';
import { ProjectKeysPage } from '@/pages/ProjectKeysPage';
import { CreateProjectPage } from '@/pages/CreateProjectPage';
import { EditProjectPage } from '@/pages/EditProjectPage';
import { ExportPage } from '@/pages/ExportPage';
import { ImportPage } from '@/pages/ImportPage';
import { PATHS } from '@/constants/paths';
import { Toaster } from '@/components/ui/sonner';

function App() {
  return (
    <Router>
      <AuthProvider>
        <TranslationEditorProvider>
          <Routes>
          <Route element={<AuthLayout />}>
            <Route path={PATHS.AUTH} element={<AuthPage />} />
          </Route>
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path={PATHS.DASHBOARD} element={<DashboardPage />} />
            <Route path={PATHS.TEAMS} element={<TeamsPage />} />
            <Route path={PATHS.TEAM_CREATE} element={<CreateTeamPage />} />
            <Route path={PATHS.PROJECT_CREATE} element={<CreateProjectPage />} />
            <Route path={PATHS.PROJECT_EDIT} element={<EditProjectPage />} />
            <Route path={PATHS.PROJECT} element={<ProjectPage />} />
            <Route path={PATHS.PROJECT_KEYS} element={<ProjectKeysPage />} />
            <Route path={PATHS.EXPORT} element={<ExportPage />} />
            <Route path={PATHS.IMPORT} element={<ImportPage />} />
          </Route>
          <Route path="*" element={<Navigate to={PATHS.HOME} replace />} />
        </Routes>
        </TranslationEditorProvider>
      </AuthProvider>
      <Toaster />
    </Router>
  );
}

export default App;
