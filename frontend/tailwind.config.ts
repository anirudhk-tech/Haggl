import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#22C55E',
          dark: '#16A34A',
          light: '#DCFCE7',
        },
        status: {
          blue: '#3B82F6',
          'blue-light': '#DBEAFE',
          orange: '#F97316',
          'orange-light': '#FFEDD5',
          yellow: '#FACC15',
          'yellow-light': '#FEF9C3',
          rose: '#F43F5E',
          'rose-light': '#FFE4E6',
          purple: '#8B5CF6',
          'purple-light': '#EDE9FE',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
export default config;

