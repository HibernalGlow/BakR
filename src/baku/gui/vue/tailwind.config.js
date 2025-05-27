/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 自定义颜色（由 CSS 变量动态设置）
        'custom': {
          100: 'var(--color-custom-100)',
          200: 'var(--color-custom-200)',
          300: 'var(--color-custom-300)',
          400: 'var(--color-custom-400)',
          500: 'var(--color-custom-500)',
          600: 'var(--color-custom-600)',
          700: 'var(--color-custom-700)',
          800: 'var(--color-custom-800)',
          900: 'var(--color-custom-900)',
        }
      },
      fontFamily: {
        'mono': ['JetBrains Mono', 'Fira Code', 'Monaco', 'Cascadia Code', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-in': 'slideIn 0.3s ease-out',
        'bounce-in': 'bounceIn 0.5s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceIn: {
          '0%': { transform: 'scale(0.3)', opacity: '0' },
          '50%': { transform: 'scale(1.05)' },
          '70%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      boxShadow: {
        'theme': '0 4px 6px -1px var(--color-custom-500, rgb(59 130 246))',
        'theme-lg': '0 10px 15px -3px var(--color-custom-500, rgb(59 130 246))',
      },
      borderColor: {
        'theme': 'var(--color-custom-500, rgb(59 130 246))',
      }
    },
  },
  plugins: [],
  
  // 暗色模式支持
  darkMode: 'class',
}