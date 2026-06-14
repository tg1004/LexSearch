import { Link } from 'react-router-dom';
import { LayoutDashboard, Scale, Shield } from 'lucide-react';
import { useState } from 'react';
import LoginModal from '../auth/LoginModal';
import SignupModal from '../auth/SignupModal';
import { useAuth } from '../../hooks/useAuth';

interface NavbarProps {
  compact?: boolean;
}

export default function Navbar({ compact = false }: NavbarProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const [showLogin, setShowLogin] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [toast, setToast] = useState('');

  return (
    <>
      <nav
        className={`flex items-center justify-between px-4 sm:px-6 py-4 w-full ${
          compact ? '' : 'max-w-6xl mx-auto'
        }`}
      >
        <Link to="/" className="flex items-center gap-2 text-primary">
          <Scale className="w-7 h-7 text-accent" />
          <span className="text-xl font-semibold tracking-tight">LexSearch</span>
        </Link>

        <div className="flex items-center gap-2 sm:gap-3">
          {isAuthenticated && user ? (
            <>
              <Link
                to="/dashboard"
                className="hidden sm:inline-flex items-center gap-1.5 px-3 py-2 text-sm text-subtext hover:text-accent transition-colors"
              >
                <LayoutDashboard className="w-4 h-4" />
                Dashboard
              </Link>
              {user.is_admin && (
                <Link
                  to="/admin"
                  className="hidden sm:inline-flex items-center gap-1.5 px-3 py-2 text-sm text-subtext hover:text-accent transition-colors"
                >
                  <Shield className="w-4 h-4" />
                  Admin
                </Link>
              )}
              <span className="text-sm text-subtext hidden md:inline max-w-[140px] truncate">
                {user.full_name || user.email}
              </span>
              <button
                onClick={() => logout()}
                className="px-3 sm:px-4 py-2 text-sm font-medium text-primary border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <button
                onClick={() => setShowLogin(true)}
                className="px-3 sm:px-4 py-2 text-sm font-medium text-primary hover:text-accent transition-colors"
              >
                Log in
              </button>
              <button
                onClick={() => setShowSignup(true)}
                className="px-3 sm:px-4 py-2 text-sm font-medium text-white bg-accent rounded-lg hover:bg-accent/90 transition-colors"
              >
                Sign up
              </button>
            </>
          )}
        </div>
      </nav>

      <LoginModal
        isOpen={showLogin}
        onClose={() => setShowLogin(false)}
        onSwitchToSignup={() => {
          setShowLogin(false);
          setShowSignup(true);
        }}
        onSuccess={() => setToast('Welcome back!')}
      />

      <SignupModal
        isOpen={showSignup}
        onClose={() => setShowSignup(false)}
        onSwitchToLogin={() => {
          setShowSignup(false);
          setShowLogin(true);
        }}
        onSuccess={() => setToast('Account created successfully!')}
      />

      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-primary text-white text-sm rounded-lg shadow-lg">
          {toast}
          <button
            type="button"
            onClick={() => setToast('')}
            className="ml-3 opacity-70 hover:opacity-100"
          >
            ×
          </button>
        </div>
      )}
    </>
  );
}
