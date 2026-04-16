/**
 * Tailwind CSS Configuration
 * ConektaBots Design System
 *
 * Use this file as reference for Next.js app setup:
 * npx create-next-app@latest --typescript
 * Then copy these customizations into your tailwind.config.ts
 *
 * File: tailwind.config.ts
 * Location: Repository root
 */

import type { Config } from 'tailwindcss'
import defaultTheme from 'tailwindcss/defaultTheme'

const config: Config = {
  // Dark mode uses CSS class strategy
  darkMode: 'class',

  // Source files for content detection
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/layouts/**/*.{js,ts,jsx,tsx,mdx}',
  ],

  theme: {
    extend: {
      // ===============================================
      // TYPOGRAPHY CONFIGURATION
      // ===============================================
      fontFamily: {
        // Primary sans-serif font
        sans: [
          'Inter',
          'ui-sans-serif',
          'system-ui',
          '-apple-system',
          'BlinkMacSystemFont',
          '"Segoe UI"',
          'Roboto',
          '"Helvetica Neue"',
          'Arial',
          '"Noto Sans"',
          'sans-serif',
          '"Apple Color Emoji"',
          '"Segoe UI Emoji"',
          '"Segoe UI Symbol"',
          '"Noto Color Emoji"',
          ...defaultTheme.fontFamily.sans,
        ],
        // Monospace for code blocks
        mono: [
          '"JetBrains Mono"',
          '"Courier New"',
          'monospace',
          ...defaultTheme.fontFamily.mono,
        ],
      },

      fontSize: {
        // Custom type scale aligned with design system
        // Scale factor: 1.25x (Perfect Fifth)
        xs: ['12px', { lineHeight: '16px', letterSpacing: '0.3px' }],
        sm: ['14px', { lineHeight: '20px', letterSpacing: '0px' }],
        base: ['16px', { lineHeight: '24px', letterSpacing: '0px' }],
        lg: ['18px', { lineHeight: '24px', letterSpacing: '0px' }],
        xl: ['20px', { lineHeight: '28px', letterSpacing: '-0.5px' }],
        '2xl': ['24px', { lineHeight: '32px', letterSpacing: '-0.5px' }],
        '3xl': ['28px', { lineHeight: '36px', letterSpacing: '-0.5px' }],
        '4xl': ['32px', { lineHeight: '40px', letterSpacing: '-0.5px' }],
        '5xl': ['40px', { lineHeight: '48px', letterSpacing: '-0.5px' }],
        '6xl': ['48px', { lineHeight: '56px', letterSpacing: '-0.5px' }],
        '7xl': ['56px', { lineHeight: '64px', letterSpacing: '-0.5px' }],
      },

      // ===============================================
      // COLOR PALETTE
      // ===============================================
      colors: {
        // Brand Primary: Blue
        blue: {
          50: '#EFF6FF',
          100: '#E0EDFF',
          200: '#C7DFFE',
          300: '#A4CAFE',
          400: '#7FB3FE',
          500: '#2563EB', // Primary brand color
          600: '#2563EB',
          700: '#1D4ED8',
          800: '#1E40AF',
          900: '#1E3A8A',
          950: '#172554',
        },

        // Brand Secondary: Purple
        purple: {
          50: '#F3F0FF',
          100: '#EBE9FE',
          200: '#DDD6FE',
          300: '#CAC3FE',
          400: '#B29EFF',
          500: '#7C3AED', // Secondary brand color
          600: '#7C3AED',
          700: '#6D28D9',
          800: '#5B21B6',
          900: '#4C1D95',
          950: '#2D1B69',
        },

        // Status: Green (Success)
        green: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          200: '#BBEF2D4',
          300: '#86EFAC',
          400: '#4ADE80',
          500: '#16A34A', // Success color
          600: '#15803D',
          700: '#166534',
          800: '#166534',
          900: '#14532D',
          950: '#051E16',
        },

        // Status: Red (Danger/Error)
        red: {
          50: '#FEF2F2',
          100: '#FEE2E2',
          200: '#FECACA',
          300: '#FCA5A5',
          400: '#F87171',
          500: '#DC2626', // Danger/Error color
          600: '#B91C1C',
          700: '#991B1B',
          800: '#7F1D1D',
          900: '#65140A',
          950: '#450A0A',
        },

        // Status: Orange (Warning)
        orange: {
          50: '#FFF7ED',
          100: '#FFEDD5',
          200: '#FED7AA',
          300: '#FDBA74',
          400: '#FB923C',
          500: '#EA580C', // Warning color
          600: '#C2410C',
          700: '#A16207',
          800: '#7C2D12',
          900: '#54210E',
          950: '#3E160B',
        },

        // Gray scale extended
        gray: {
          50: '#F9FAFB',
          100: '#F3F4F6',
          200: '#E5E7EB',
          300: '#D1D5DB',
          400: '#9CA3AF',
          500: '#6B7280',
          600: '#4B5563', // Primary text (light mode)
          700: '#374151',
          800: '#1F2937',
          900: '#111827', // Headings (light mode)
          950: '#030712', // Background (dark mode)
        },

        // Semantic colors
        success: '#16A34A',
        warning: '#EA580C',
        error: '#DC2626',
        danger: '#DC2626',
        info: '#2563EB',
      },

      // ===============================================
      // SPACING SYSTEM (8px base grid)
      // ===============================================
      spacing: {
        // 8px base unit (px-1 = 4px, px-2 = 8px, px-4 = 16px)
        // Tailwind defaults already aligned with 8px grid
        // Extended custom spacing if needed:
        '18': '4.5rem', // 72px
        '22': '5.5rem', // 88px
        '26': '6.5rem', // 104px
        '30': '7.5rem', // 120px
      },

      // ===============================================
      // BORDER RADIUS
      // ===============================================
      borderRadius: {
        // Design system radius scale
        'none': '0px',
        'xs': '2px',
        'sm': '4px',
        'base': '6px',
        'md': '8px',
        'lg': '12px',
        'xl': '16px',
        'full': '9999px',
      },

      // ===============================================
      // SHADOWS & ELEVATION
      // ===============================================
      boxShadow: {
        // Professional shadow system
        'none': 'none',
        'sm': '0 1px 2px rgb(0 0 0 / 0.05)',
        'base': '0 1px 3px rgb(0 0 0 / 0.1), 0 1px 2px rgb(0 0 0 / 0.06)',
        'md': '0 4px 6px rgb(0 0 0 / 0.1)',
        'lg': '0 10px 15px rgb(0 0 0 / 0.1), 0 4px 6px rgb(0 0 0 / 0.05)',
        'xl': '0 20px 25px rgb(0 0 0 / 0.1), 0 8px 10px rgb(0 0 0 / 0.04)',
        '2xl': '0 25px 50px rgb(0 0 0 / 0.15)',

        // Dark mode shadows (more subtle)
        'dark-sm': '0 1px 2px rgb(0 0 0 / 0.15)',
        'dark-md': '0 4px 6px rgb(0 0 0 / 0.2)',
        'dark-lg': '0 10px 15px rgb(0 0 0 / 0.25)',

        // Focus rings (semantic use)
        'focus': '0 0 0 3px rgb(255 255 255 / 0.5), 0 0 0 5px rgb(37 99 235 / 1)',
        'focus-dark': '0 0 0 3px rgb(17 24 39 / 0.5), 0 0 0 5px rgb(37 99 235 / 1)',
      },

      // ===============================================
      // TRANSITIONS
      // ===============================================
      transitionDuration: {
        // Standard animation timings
        'fast': '150ms',
        'standard': '200ms',
        'slow': '300ms',
      },

      transitionTimingFunction: {
        'ease-out': 'cubic-bezier(0, 0, 0.2, 1)', // Component appears
        'ease-in': 'cubic-bezier(0.4, 0, 1, 1)', // Component disappears
        'ease-in-out': 'cubic-bezier(0.4, 0, 0.2, 1)', // Standard motion
      },

      // ===============================================
      // KEYFRAME ANIMATIONS
      // ===============================================
      keyframes: {
        // Entrance animations
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(-8px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-in-left': {
          '0%': { transform: 'translateX(-8px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
        'slide-in-right': {
          '0%': { transform: 'translateX(8px)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },

        // Looping animations
        'spin-slow': {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        'pulse-gentle': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '.7' },
        },
        'bounce-subtle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-2px)' },
        },
      },

      animation: {
        // Animation utilities
        'fade-in': 'fade-in 200ms ease-in-out',
        'slide-up': 'slide-up 200ms ease-out',
        'slide-down': 'slide-down 200ms ease-out',
        'slide-in-left': 'slide-in-left 200ms ease-out',
        'slide-in-right': 'slide-in-right 200ms ease-out',
        'spin-slow': 'spin-slow 3s linear infinite',
        'pulse-gentle': 'pulse-gentle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-subtle': 'bounce-subtle 1s ease-in-out infinite',
      },

      // ===============================================
      // CONTAINER QUERIES
      // ===============================================
      container: {
        center: true,
        padding: {
          DEFAULT: '1rem',
          sm: '2rem',
          lg: '4rem',
          xl: '5rem',
          '2xl': '6rem',
        },
      },

      // ===============================================
      // Z-INDEX SCALE (Stacking context)
      // ===============================================
      zIndex: {
        'dropdown': '50',
        'sticky': '20',
        'fixed': '30',
        'modal-backdrop': '40',
        'modal': '50',
        'popover': '60',
        'tooltip': '70',
        'notification': '80',
      },
    },
  },

  plugins: [
    // Plugin: Focus visible (custom focus ring)
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),

    // Custom plugin: Utility functions
    function addCustomUtilities({ addUtilities }: any) {
      const customUtilities = {
        // Text truncation with ellipsis
        '.truncate-1': {
          '@apply overflow-hidden text-ellipsis whitespace-nowrap': {},
        },
        '.truncate-2': {
          'display': '-webkit-box',
          '-webkit-line-clamp': '2',
          '-webkit-box-orient': 'vertical',
          'overflow': 'hidden',
        },
        '.truncate-3': {
          'display': '-webkit-box',
          '-webkit-line-clamp': '3',
          '-webkit-box-orient': 'vertical',
          'overflow': 'hidden',
        },

        // Flex utilities
        '.flex-center': {
          '@apply flex items-center justify-center': {},
        },
        '.flex-between': {
          '@apply flex items-center justify-between': {},
        },

        // Grid utilities
        '.grid-auto-fit': {
          '@apply grid auto-cols-max gap-4': {},
        },

        // Responsive text sizing
        '.responsive-heading': {
          '@apply text-2xl sm:text-3xl md:text-4xl lg:text-5xl font-bold': {},
        },

        // Focus ring styling
        '.focus-ring': {
          '@apply outline-none ring-2 ring-blue-500 ring-offset-2': {},
        },

        // Disabled state
        '.disabled-input': {
          '@apply bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 cursor-not-allowed': {},
        },

        // Hover elevation
        '.hover-lift': {
          '@apply transition-all duration-200 hover:-translate-y-1 hover:shadow-lg': {},
        },

        // Transition utilities
        '.transition-fast': {
          '@apply transition duration-150 ease-out': {},
        },
        '.transition-standard': {
          '@apply transition duration-200 ease-in-out': {},
        },
        '.transition-slow': {
          '@apply transition duration-300 ease-in-out': {},
        },
      }

      addUtilities(customUtilities)
    },
  ],
}

export default config
