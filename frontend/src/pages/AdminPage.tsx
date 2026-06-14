import { useQuery } from '@tanstack/react-query';
import Navbar from '../components/shared/Navbar';
import AdminDashboard from '../components/admin/AdminDashboard';
import ErrorMessage from '../components/shared/ErrorMessage';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import { getAdminStats } from '../api/adminApi';

export default function AdminPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['admin', 'stats'],
    queryFn: getAdminStats,
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100">
        <Navbar compact />
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-primary">Admin Dashboard</h1>
          <p className="text-subtext mt-1">Search analytics and system health</p>
        </div>

        {isLoading && (
          <div className="flex justify-center py-20">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {error && (
          <ErrorMessage
            message={error instanceof Error ? error.message : 'Failed to load admin stats'}
          />
        )}

        {data && <AdminDashboard stats={data} />}
      </main>
    </div>
  );
}
