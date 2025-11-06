import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@app': '/src/app',
      '@components': '/src/components',
      '@features': '/src/features',
      '@state': '/src/state',
      '@styles': '/src/styles',
      '@mock': '/src/mock',
      '@lib': '/src/lib'
    }
  },
  server: {
    port: 5173
  },
  preview: {
    port: 5173
  }
});

