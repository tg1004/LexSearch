import { useEffect } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import * as authApi from '../api/authApi';
import { useAuthStore } from '../store/authStore';
import type { LoginPayload, SignupPayload } from '../types/auth.types';

export function useAuth() {
  const queryClient = useQueryClient();
  const { token, user, setAuth, clearAuth } = useAuthStore();

  const meQuery = useQuery({
    queryKey: ['auth', 'me', token],
    queryFn: () => authApi.getMe(token!),
    enabled: !!token,
    retry: false,
  });

  useEffect(() => {
    if (meQuery.data && token) {
      setAuth(token, meQuery.data);
    }
    if (meQuery.isError) {
      clearAuth();
    }
  }, [meQuery.data, meQuery.isError, token, setAuth, clearAuth]);

  const signupMutation = useMutation({
    mutationFn: (payload: SignupPayload) => authApi.signup(payload),
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
      queryClient.setQueryData(['auth', 'me', data.access_token], data.user);
    },
  });

  const loginMutation = useMutation({
    mutationFn: (payload: LoginPayload) => authApi.login(payload),
    onSuccess: (data) => {
      setAuth(data.access_token, data.user);
      queryClient.setQueryData(['auth', 'me', data.access_token], data.user);
    },
  });

  const logout = async () => {
    try {
      await authApi.logout();
    } finally {
      clearAuth();
      queryClient.removeQueries({ queryKey: ['auth'] });
    }
  };

  return {
    token,
    user: user || meQuery.data || null,
    isAuthenticated: !!token && !!(user || meQuery.data),
    isLoading: meQuery.isLoading,
    signup: signupMutation.mutateAsync,
    login: loginMutation.mutateAsync,
    logout,
    signupError: signupMutation.error,
    loginError: loginMutation.error,
    isSigningUp: signupMutation.isPending,
    isLoggingIn: loginMutation.isPending,
  };
}
