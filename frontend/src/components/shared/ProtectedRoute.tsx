import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth';
import LoadingSpinner from './LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  adminOnly?: boolean;
}

export default function ProtectedRoute({ children, adminOnly = false }: ProtectedRouteProps) {
  const { isLoading, user, token } = useAuth();
  const location = useLocation();

  if (isLoading && token) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!token) {
    return <Navigate to="/" replace state={{ from: location.pathname }} />;
  }

  if (adminOnly && !user?.is_admin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}
