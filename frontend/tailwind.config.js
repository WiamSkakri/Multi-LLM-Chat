/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Courier New"', 'Courier', 'monospace'],
      },
      colors: {
        'gpt-blue': '#10a37f',
        'claude-purple': '#d97757',
        'gemini-green': '#4285f4',
        'local-orange': '#f97316',
      },
    },
  },
  plugins: [],
}

