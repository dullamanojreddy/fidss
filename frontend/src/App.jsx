import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Layout } from './components/Layout';
import { ScreeningConsolePage } from './pages/ScreeningConsolePage';
import { DashboardPage } from './pages/DashboardPage';
import { OfficerReviewPage } from './pages/OfficerReviewPage';
import { AuditTrailPage } from './pages/AuditTrailPage';
import { WatchlistPage } from './pages/WatchlistPage';
import { DuplicateIdentityPage } from './pages/DuplicateIdentityPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { SystemSettingsPage } from './pages/SystemSettingsPage';
import { LoginPage } from './pages/LoginPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          {/* Authenticated Layout */}
          <Route element={<Layout />}>
            <Route path="/" element={<Navigate to="/screening-console" replace />} />
            <Route path="/screening-console" element={<ScreeningConsolePage />} />
            <Route path="/screening-console/:id" element={<ScreeningConsolePage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/officer-review" element={<OfficerReviewPage />} />
            <Route path="/officer-review/:id" element={<OfficerReviewPage />} />
            <Route path="/audit-trail" element={<AuditTrailPage />} />
            <Route path="/audit-trail/:id" element={<AuditTrailPage />} />
            <Route path="/watchlist" element={<WatchlistPage />} />
            <Route path="/duplicate-identity" element={<DuplicateIdentityPage />} />
            <Route path="/documents" element={<DocumentsPage />} />
            <Route path="/reports" element={<DashboardPage />} />
            <Route path="/settings" element={<SystemSettingsPage />} />
          </Route>

          <Route path="*" element={<Navigate to="/screening-console" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
