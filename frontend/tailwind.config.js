/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        agro: {
          50: "#f2f9f3",
          100: "#e1f2e4",
          200: "#c5e5cc",
          300: "#99d2a5",
          400: "#67b777",
          500: "#419c52",
          600: "#317f40",
          700: "#286534",
          800: "#23502c",
          900: "#1d4226",
          950: "#0c2413",
        },
      },
    },
  },
  plugins: [],
};
