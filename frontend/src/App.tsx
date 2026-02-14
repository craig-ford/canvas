import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import CanvasPage from './canvas/CanvasPage';
import { ReviewWizard } from './reviews';

function App() {
  return (
    <Router>
      <AppShell>
        <Routes>
          <Route path="/vbus/:id" element={<CanvasPage />} />
          <Route path="/vbus/:id/review/new" element={<ReviewWizard />} />
          <Route path="/" element={
            <div className="px-4 py-6 sm:px-0">
              <div className="border-4 border-dashed border-gray-200 rounded-lg h-96 flex items-center justify-center">
                <p className="text-gray-500">Canvas application placeholder</p>
              </div>
            </div>
          } />
        </Routes>
      </AppShell>
    </Router>
  );
}

export default App;