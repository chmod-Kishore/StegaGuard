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
        matrix: {
          DEFAULT: '#00FF41',
          dim: '#008F11',
          dark: '#003B00'
        },
        panel: '#0C130E',
        alert: '#EF4444',
        background: '#000000',
        foreground: '#E0E0E0',
        dim: '#94A3B8',
        border: '#1F2937'
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
        mono: ['var(--font-mono)', 'monospace'],
      },
      keyframes: {
        flicker: {
          '0%, 19.999%, 22%, 62.999%, 64%, 64.999%, 70%, 100%': { opacity: '1' },
          '20%, 21.999%, 63%, 63.999%, 65%, 69.999%': { opacity: '0.4' },
        },
        glitch: {
          '0%': { transform: 'translate(0)' },
          '20%': { transform: 'translate(-2px, 1px)' },
          '40%': { transform: 'translate(-1px, -1px)' },
          '60%': { transform: 'translate(2px, 1px)' },
          '80%': { transform: 'translate(1px, -1px)' },
          '100%': { transform: 'translate(0)' }
        },
        scanline: {
          '0%': { transform: 'translateY(-100%)' },
          '100%': { transform: 'translateY(100%)' }
        },
        typing: {
          'from': { width: '0' },
          'to': { width: '100%' }
        }
      },
      animation: {
        'flicker': 'flicker 3s linear infinite',
        'glitch': 'glitch 0.2s ease-in-out',
        'scanline': 'scanline 8s linear infinite',
        'typing': 'typing 2s steps(40, end)'
      },
      backgroundImage: {
        'grid-pattern': 'linear-gradient(to right, #00FF4111 1px, transparent 1px), linear-gradient(to bottom, #00FF4111 1px, transparent 1px)'
      }
    },
  },
  plugins: [],
};
export default config;
