import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'brand-blue': {
          DEFAULT: '#1e3a8a',
          light: '#2563eb',
        },
        'brand-green': {
          DEFAULT: '#047857',
          light: '#059669',
        },
        'brand-orange': {
          DEFAULT: '#f97316',
          light: '#fb923c',
        },
        'neutral': {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        },
      },
      keyframes: {
        'listening-pulse': {
          '0%': { transform: 'scale(0.6)', opacity: '0.7' },
          '100%': { transform: 'scale(1.4)', opacity: '0' },
        },
        'wave-listening': {
          '0%, 100%': { height: '25%' },
          '50%': { height: '75%' },
        },
        'wave-speaking': {
          '0%, 100%': { height: '10%' },
          '25%': { height: '100%' },
          '50%': { height: '50%' },
          '75%': { height: '80%' },
        },
        'wave-thinking': {
          '0%, 100%': { transform: 'scaleY(0.7)' },
          '50%': { transform: 'scaleY(1)' },
        },
      },
      animation: {
        'listening-pulse': 'listening-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'wave-listening': 'wave-listening 1.5s ease-in-out infinite',
        'wave-speaking': 'wave-speaking 0.8s ease-in-out infinite',
        'wave-thinking': 'wave-thinking 1s ease-in-out infinite',
      },
    },
  },
  plugins: [],
};

export default config;