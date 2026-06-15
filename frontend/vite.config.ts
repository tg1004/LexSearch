import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig(({ mode }) => {
  // Load root .env (VITE_* vars live in project root .env)
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '');
  const apiTarget = env.VITE_API_URL || 'http://127.0.0.1:8000';

  return {
    plugins: [react()],
    envDir: path.resolve(__dirname, '..'),
    server: {
      port: 3000,
      host: true,
      // Proxy /api to backend — avoids CORS and wrong-host issues in local dev
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
        },
      },
    },
  };
});
