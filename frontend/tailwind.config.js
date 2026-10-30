/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        space: {
          950: '#07090E',
          900: '#0B0D14',
          850: '#0F121C',
          800: '#141824',
          750: '#1A2030',
          700: '#22283C',
          600: '#2E3650',
          500: '#475569',
        },
        brand: {
          purple: '#8B5CF6',
          indigo: '#6366F1',
          violet: '#7C3AED',
          cyan: '#06B6D4',
          emerald: '#10B981',
          amber: '#F59E0B',
          rose: '#EF4444',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      }
    },
  },
  plugins: [],
}
