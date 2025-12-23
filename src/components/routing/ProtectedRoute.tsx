import { Navigate } from 'react-router-dom';
import { useAuth } from '@state/auth';

type Role = 'student' | 'company' | 'admin';

export function ProtectedRoute(props: { allow: Role[]; children: React.ReactNode }) {
  const { user } = useAuth();
  if (!user) return <Navigate to="/login" replace />;
  if (!props.allow.includes(user.role)) return <Navigate to={`/${user.role}`} replace />;
  return <>{props.children}</>;
}
