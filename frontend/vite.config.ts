import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import importMetaUrlPlugin from '@codingame/esbuild-import-meta-url-plugin';

// https://vitejs.dev/config/
export default defineConfig({
  base: process.env.BASE ?? '/',
  plugins: [react()],
  server: {
    host: true
  },

  optimizeDeps: {
    esbuildOptions: {
      plugins: [
        importMetaUrlPlugin
      ]
    }
  }
})