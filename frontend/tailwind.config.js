/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./pages/**/*.{js,jsx,mdx}", "./components/**/*.{js,jsx,mdx}", "./app/**/*.{js,jsx,mdx}"],
    theme: {
      extend: {
        colors: {
          blue: {
            500: "#3B82F6",
            600: "#2563EB",
          },
          green: {
            500: "#22C55E",
            600: "#16A34A",
          },
          pink: {
            500: "#EC4899",
            600: "#DB2777",
          },
          purple: {
            500: "#A855F7",
            600: "#9333EA",
          },
        },
      },
    },
    plugins: [],
  }
  
  