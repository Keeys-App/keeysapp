import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';
import { AuthPage } from './pages/AuthPage';
import { DashboardPage } from './pages/DashboardPage';
import { ProjectPage } from './pages/ProjectPage';
import { PATHS } from './constants/paths';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path={PATHS.AUTH} element={<AuthPage />} />
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path={PATHS.DASHBOARD} element={<DashboardPage />} />
            <Route path={PATHS.PROJECT} element={<ProjectPage />} />
          </Route>
          <Route path="*" element={<Navigate to={PATHS.HOME} replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
