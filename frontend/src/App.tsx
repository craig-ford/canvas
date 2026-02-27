import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams } from 'react-router-dom';
import { AuthProvider } from './auth/useAuth';
import { useAuth } from './auth/useAuth';
import { LoginPage } from './auth/LoginPage';
import { ResetPasswordPage } from './auth/ResetPasswordPage';
import { AppShell } from './components/AppShell';
import ErrorBoundary from './components/ErrorBoundary';
import CanvasPage from './canvas/CanvasPage';
import { ReviewWizard } from './reviews';
import { DashboardPage } from './dashboard/DashboardPage';
import { UsersPage } from './admin/UsersPage';
import HelpPage from './help/HelpPage';

function VBURedirect() {
  const { vbuId } = useParams();
  return <Navigate to={`/vbus/${vbuId}/canvas`} replace />;
}

function AuthenticatedApp() {
  const { user, isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <LoginPage />;
  }

  if (user?.must_reset_password) {
    return <ResetPasswordPage />;
  }

  return (
    <AppShell>
      <Routes>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/admin/users" element={user?.role === 'admin' ? <UsersPage /> : <Navigate to="/dashboard" replace />} />
        <Route path="/help" element={<HelpPage />} />
        <Route path="/vbus/:vbuId/canvas" element={<CanvasPage />} />
        <Route path="/vbus/:vbuId" element={<VBURedirect />} />
        <Route path="/vbus/:id/review/new" element={<ReviewWizard />} />
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </AppShell>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <AuthenticatedApp />
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;
