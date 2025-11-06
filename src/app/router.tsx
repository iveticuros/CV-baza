import { createBrowserRouter, Navigate } from 'react-router-dom';
import { LoginPage } from '@features/auth/LoginPage';
import { CompanyDashboard } from '@features/company/CompanyDashboard';
import { StudentDashboard } from '@features/student/StudentDashboard';
import { AdminDashboard } from '@features/admin/AdminDashboard';
import { AppLayout } from '@components/layout/AppLayout';
import { ProtectedRoute } from '@components/routing/ProtectedRoute';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/login" replace />
  },
  {
    path: '/login',
    element: <LoginPage />
  },
  {
    element: <AppLayout />,
    children: [
      {
        path: '/company',
        element: (
          <ProtectedRoute allow={['company']}>
            <CompanyDashboard />
          </ProtectedRoute>
        )
      },
      {
        path: '/student',
        element: (
          <ProtectedRoute allow={['student']}>
            <StudentDashboard />
          </ProtectedRoute>
        )
      },
      {
        path: '/admin',
        element: (
          <ProtectedRoute allow={['admin']}>
            <AdminDashboard />
          </ProtectedRoute>
        )
      }
    ]
  }
]);

