/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        telegram: {
          bg: 'var(--tg-theme-bg-color, #ffffff)',
          secondaryBg: 'var(--tg-theme-secondary-bg-color, #f4f4f5)',
          text: 'var(--tg-theme-text-color, #18181b)',
          hint: 'var(--tg-theme-hint-color, #71717a)',
          link: 'var(--tg-theme-link-color, #2563eb)',
          button: 'var(--tg-theme-button-color, #2563eb)',
          buttonText: 'var(--tg-theme-button-text-color, #ffffff)',
        }
      }
    },
  },
  plugins: [],
}
