/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4F46E5',
          dark: '#3730A3',
          light: '#818CF8',
        },
        secondary: {
          DEFAULT: '#14B8A6',
          dark: '#0F766E',
          light: '#5EEAD4',
        },
        background: {
          DEFAULT: '#F3F4F6',
          dark: '#1F2937',
        },
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: [
      {
        intellipath: {
          "primary": "#4F46E5",
          "secondary": "#14B8A6",
          "accent": "#F97316",
          "neutral": "#1F2937",
          "base-100": "#F3F4F6",
          "info": "#3ABFF8",
          "success": "#22C55E",
          "warning": "#F59E0B",
          "error": "#EF4444",
        },
      },
    ],
  },
}