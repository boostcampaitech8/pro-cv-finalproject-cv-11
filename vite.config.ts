import { defineConfig } from 'vite'
import path from 'path'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    // The React and Tailwind plugins are both required for Make, even if
    // Tailwind is not being actively used – do not remove them
    react(),
    tailwindcss(),
  ],
  resolve: {
    alias: {
      // Alias @ to the src directory
      '@': path.resolve(__dirname, './src'),
    },
  },

  // ⭐ 여기 추가
  server: {
    port: 3000,       // 원하는 포트 (5173 유지하고 싶으면 이 줄 제거)
    strictPort: true, // 해당 포트 못 쓰면 에러
  },
})
