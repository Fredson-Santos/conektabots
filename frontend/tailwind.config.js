/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#2563eb',
        secondary: '#64748b',
      },
      spacing: {
        'xs': '4px',    // 8px grid (half)
        'sm': '8px',    // 8px grid
        'md': '16px',   // 8px grid (2x)
        'lg': '24px',   // 8px grid (3x)
        'xl': '32px',   // 8px grid (4x)
        '2xl': '48px',  // 8px grid (6x)
      },
      borderRadius: {
        'sm': '4px',
        'md': '6px',
        'lg': '8px',
        'xl': '12px',
      },
    },
  },
  plugins: [],
}
