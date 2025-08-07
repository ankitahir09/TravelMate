import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // this exposes it to your local network
    port: 5173       // or whatever port you're using
  },
  optimizeDeps: {
    include: ['@shadergradient/react'],
  },
})
