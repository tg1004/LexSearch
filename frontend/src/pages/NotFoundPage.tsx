import { Link } from 'react-router-dom';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center">
      <h1 className="text-6xl font-bold text-primary mb-2">404</h1>
      <p className="text-subtext mb-6">Page not found</p>
      <Link
        to="/"
        className="px-4 py-2 text-sm font-medium text-white bg-accent rounded-lg hover:bg-accent/90 transition-colors"
      >
        Back to home
      </Link>
    </div>
  );
}
