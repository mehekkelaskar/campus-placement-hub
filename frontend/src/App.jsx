import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';

// Auth pages
import LoginPage from './pages/auth/LoginPage';
import RegisterPage from './pages/auth/RegisterPage';
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage';

// Student pages
import DashboardPage from './pages/student/DashboardPage';
import CompaniesPage from './pages/student/CompaniesPage';
import CompanyDetailPage from './pages/student/CompanyDetailPage';
import BookmarksPage from './pages/student/BookmarksPage';
import DriveTimelinePage from './pages/student/DriveTimelinePage';

// Admin pages
import AdminDashboardPage from './pages/admin/AdminDashboardPage';
import AdminCompaniesPage from './pages/admin/AdminCompaniesPage';
import AdminStudentsPage from './pages/admin/AdminStudentsPage';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Auth routes */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />

          {/* Student routes */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Layout><DashboardPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/companies" element={
            <ProtectedRoute>
              <Layout><CompaniesPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/companies/:id" element={
            <ProtectedRoute>
              <Layout><CompanyDetailPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/bookmarks" element={
            <ProtectedRoute>
              <Layout><BookmarksPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/drives" element={
            <ProtectedRoute>
              <Layout><DriveTimelinePage /></Layout>
            </ProtectedRoute>
          } />

          {/* Admin routes */}
          <Route path="/admin/dashboard" element={
            <ProtectedRoute adminOnly>
              <Layout><AdminDashboardPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/admin/companies" element={
            <ProtectedRoute adminOnly>
              <Layout><AdminCompaniesPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/admin/students" element={
            <ProtectedRoute adminOnly>
              <Layout><AdminStudentsPage /></Layout>
            </ProtectedRoute>
          } />
          <Route path="/admin/drives" element={
            <ProtectedRoute adminOnly>
              <Layout><DriveTimelinePage /></Layout>
            </ProtectedRoute>
          } />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/login" replace />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
