import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 2300,  // 프론트엔드 포트 2300으로 변경
    host: true
  },
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
