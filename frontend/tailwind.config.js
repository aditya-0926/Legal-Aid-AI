/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1a4f8a',
          light: '#2563eb',
          dark: '#0f2d50',
        },
        accent: { DEFAULT: '#f97316' },
        surface: { DEFAULT: '#f8fafc' },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        display: ['Merriweather', 'serif'],
      },
    },
  },
  plugins: [],
}
