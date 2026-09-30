/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Sleek modern primary colors for premium look
        brand: {
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc8fc',
          400: '#38acf8',
          500: '#0e91eb',
          600: '#0273c7',
          700: '#035ca1',
          800: '#074e85',
          900: '#0c426e',
          950: '#082a49',
        }
      }
    },
  },
  plugins: [],
}
