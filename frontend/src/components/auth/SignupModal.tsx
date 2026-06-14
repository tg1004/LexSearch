import { FormEvent, useState } from 'react';
import { X } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import ErrorMessage from '../shared/ErrorMessage';
import LoadingSpinner from '../shared/LoadingSpinner';

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
  onSuccess: () => void;
}

export default function SignupModal({ isOpen, onClose, onSwitchToLogin, onSuccess }: SignupModalProps) {
  const { signup, isSigningUp, signupError } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  if (!isOpen) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await signup({ email, password, full_name: fullName });
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Signup failed');
    }
  };

  const displayError = error || (signupError instanceof Error ? signupError.message : '');

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40">
      <div className="w-full max-w-md bg-white rounded-xl shadow-xl">
        <div className="flex items-center justify-between px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-primary">Create account</h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600" aria-label="Close">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {displayError && <ErrorMessage message={displayError} />}

          <div>
            <label htmlFor="signup-name" className="block text-sm font-medium text-gray-700 mb-1">
              Full name
            </label>
            <input
              id="signup-name"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent"
              placeholder="Your name"
            />
          </div>

          <div>
            <label htmlFor="signup-email" className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              id="signup-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label htmlFor="signup-password" className="block text-sm font-medium text-gray-700 mb-1">
              Password
            </label>
            <input
              id="signup-password"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent"
              placeholder="At least 8 characters"
            />
          </div>

          <button
            type="submit"
            disabled={isSigningUp}
            className="w-full flex items-center justify-center gap-2 py-2.5 text-sm font-medium text-white bg-accent rounded-lg hover:bg-accent/90 disabled:opacity-60 transition-colors"
          >
            {isSigningUp ? <LoadingSpinner size="sm" /> : null}
            Create account
          </button>
        </form>

        <p className="px-6 pb-6 text-sm text-subtext text-center">
          Already have an account?{' '}
          <button onClick={onSwitchToLogin} className="text-accent font-medium hover:underline">
            Log in
          </button>
        </p>
      </div>
    </div>
  );
}
