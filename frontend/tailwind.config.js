/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#2d6a4f',
          800: '#1b4332',
          900: '#081c15',
          950: '#040d0a',
        },
        cream: {
          50: '#ffffff',
          100: '#fdfbf7',
          200: '#f8f5ee',
          300: '#f1ece0',
          400: '#e5dcce',
          500: '#d8cbba',
        },
        sand: {
          100: '#fefae0',
          200: '#f7ebc2',
          300: '#e9d8a6',
          400: '#ddb892',
          500: '#d4a373',
          600: '#b08968',
        },
        skycoast: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9',
          600: '#0284c7',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', 'sans-serif'],
        serif: ['Playfair Display', 'Georgia', 'serif'],
      },
      boxShadow: {
        'soft-sm': '0 2px 8px -1px rgba(15, 23, 42, 0.05), 0 1px 3px -1px rgba(15, 23, 42, 0.03)',
        'soft-md': '0 8px 24px -4px rgba(15, 23, 42, 0.07), 0 4px 8px -2px rgba(15, 23, 42, 0.03)',
        'soft-lg': '0 16px 36px -6px rgba(15, 23, 42, 0.08), 0 8px 16px -4px rgba(15, 23, 42, 0.04)',
        'soft-xl': '0 24px 48px -12px rgba(15, 23, 42, 0.12), 0 12px 24px -6px rgba(15, 23, 42, 0.06)',
      }
    },
  },
  plugins: [],
}

