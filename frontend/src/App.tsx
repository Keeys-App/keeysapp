import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, TranslationEditorProvider } from '@/contexts';
import { ProtectedRoute, Layout, AuthLayout } from '@/components/layout';
import { AuthPage } from '@/pages/AuthPage';
import { DashboardPage } from '@/pages/DashboardPage';
import { OnboardingPage } from '@/pages/OnboardingPage';
import { TeamsPage } from '@/pages/TeamsPage';
import { TeamPage } from '@/pages/TeamPage';
import { TeamLogsPage } from '@/pages/TeamLogsPage';
import { CreateTeamPage } from '@/pages/CreateTeamPage';
import { EditTeamPage } from '@/pages/EditTeamPage';
import { ProjectPage } from '@/pages/ProjectPage';
import { ProjectKeysPage } from '@/pages/ProjectKeysPage';
import { CreateProjectPage } from '@/pages/CreateProjectPage';
import { EditProjectPage } from '@/pages/EditProjectPage';
import { ExportPage } from '@/pages/ExportPage';
import { ImportPage } from '@/pages/ImportPage';
import { InvitePage } from '@/pages/InvitePage';
import { ForgotPasswordPage } from '@/pages/ForgotPasswordPage';
import { ResetPasswordPage } from '@/pages/ResetPasswordPage';
import { ProfilePage } from '@/pages/ProfilePage';
import { GitHubCallbackPage } from '@/pages/GitHubCallbackPage';
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
            <Route path={PATHS.FORGOT_PASSWORD} element={<ForgotPasswordPage />} />
            <Route path={PATHS.RESET_PASSWORD} element={<ResetPasswordPage />} />
          </Route>
          <Route element={<AuthLayout />}>
            <Route path={PATHS.INVITE} element={<InvitePage />} />
          </Route>
          {/* GitHub OAuth callback - requires auth */}
          <Route
            path={PATHS.GITHUB_CALLBACK}
            element={
              <ProtectedRoute>
                <GitHubCallbackPage />
              </ProtectedRoute>
            }
          />
          <Route
            path={PATHS.ONBOARDING}
            element={
              <ProtectedRoute>
                <OnboardingPage />
              </ProtectedRoute>
            }
          />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path={PATHS.DASHBOARD} element={<DashboardPage />} />
            <Route path={PATHS.PROFILE} element={<ProfilePage />} />
            <Route path={PATHS.TEAMS} element={<TeamsPage />} />
            <Route path={PATHS.TEAM} element={<TeamPage />} />
            <Route path={PATHS.TEAM_LOGS} element={<TeamLogsPage />} />
            <Route path={PATHS.TEAM_CREATE} element={<CreateTeamPage />} />
            <Route path={PATHS.TEAM_EDIT} element={<EditTeamPage />} />
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
