import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#139187',
          50: '#e5f4f2',
          100: '#cceae6',
          200: '#99d5cd',
          300: '#66c0b4',
          400: '#33ab9b',
          500: '#139187',
          600: '#0f736b',
          700: '#0b5550',
          800: '#073734',
          900: '#041a19'
        },
        background: 'rgb(var(--bg) / <alpha-value>)',
        foreground: 'rgb(var(--fg) / <alpha-value>)',
        muted: 'rgb(var(--muted) / <alpha-value>)',
        card: 'rgb(var(--card) / <alpha-value>)',
        glow: 'rgb(var(--glow) / <alpha-value>)',
      },
      borderRadius: {
        xl: 'var(--radius)',
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(19,145,135,.14), 0 8px 30px rgba(19,145,135,.18)',
        'glow-dark': '0 0 0 1px rgba(255,255,255,.06), 0 8px 30px rgba(19,145,135,.28)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        heading: ['Poppins', 'Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.2s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'glow-pulse': 'glowPulse 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        glowPulse: {
          '0%, 100%': { boxShadow: '0 0 0 1px rgba(19,145,135,.14), 0 8px 30px rgba(19,145,135,.18)' },
          '50%': { boxShadow: '0 0 0 1px rgba(19,145,135,.24), 0 8px 30px rgba(19,145,135,.28)' },
        },
      },
    },
  },
  plugins: [],
}

export default config
