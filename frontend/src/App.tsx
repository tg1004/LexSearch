import { Route, Routes } from 'react-router-dom';
import ProtectedRoute from './components/shared/ProtectedRoute';
import AdminPage from './pages/AdminPage';
import DashboardPage from './pages/DashboardPage';
import DocumentPage from './pages/DocumentPage';
import HomePage from './pages/HomePage';
import NotFoundPage from './pages/NotFoundPage';
import SearchResultsPage from './pages/SearchResultsPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/search" element={<SearchResultsPage />} />
      <Route path="/document/:documentId" element={<DocumentPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin"
        element={
          <ProtectedRoute adminOnly>
            <AdminPage />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
