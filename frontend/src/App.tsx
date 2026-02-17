import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './auth/useAuth';
import { AppShell } from './components/AppShell';
import CanvasPage from './canvas/CanvasPage';
import { ReviewWizard } from './reviews';
import { DashboardPage } from './dashboard/DashboardPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppShell>
          <Routes>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/vbus/:vbuId/canvas" element={<CanvasPage />} />
            <Route path="/vbus/:id/review/new" element={<ReviewWizard />} />
            <Route path="/" element={<DashboardPage />} />
          </Routes>
        </AppShell>
      </Router>
    </AuthProvider>
  );
}

export default App;