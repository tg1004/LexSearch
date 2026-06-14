import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import ErrorMessage from '../shared/ErrorMessage';
import LoadingSpinner from '../shared/LoadingSpinner';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToSignup: () => void;
  onSuccess: () => void;
}

export default function LoginModal({ isOpen, onClose, onSwitchToSignup, onSuccess }: LoginModalProps) {
  const { login, isLoggingIn, loginError } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login({ email, password });
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    }
  };

  const displayError = error || (loginError instanceof Error ? loginError.message : '');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="w-full max-w-md bg-white rounded-xl shadow-xl">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-primary">Log in</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {displayError && <ErrorMessage message={displayError} />}

          <div>
            <label htmlFor="login-email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="login-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="login-password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="login-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={isLoggingIn}
            className="w-full flex items-center justify-center gap-2 py-2.5 text-sm font-medium text-white bg-accent rounded-lg hover:bg-accent/90 disabled:opacity-60 transition-colors"
          >
            {isLoggingIn ? <LoadingSpinner size="sm" /> : null}
            Log in
          </button>
        </form>

        <p className="px-6 pb-6 text-sm text-subtext text-center">
          Don&apos;t have an account?{' '}
          <button onClick={onSwitchToSignup} className="text-accent font-medium hover:underline">
            Sign up
          </button>
        </p>
      </div>
    </div>
  );
}
