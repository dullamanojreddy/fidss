/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        fidss: {
          blue: "#2563EB",
          darkblue: "#1E40AF",
          surface: "#F8FAFC",
        }
      }
    },
  },
  plugins: [],
}
