/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        axioma: '#FFD700',
        veridicus: '#4169E1',
        paradoxia: '#FF00FF',
      },
    },
  },
  plugins: [],
}
