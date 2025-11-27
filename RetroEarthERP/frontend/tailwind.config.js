/** @type {import('tailwindcss').Config} */
const colors = require('tailwindcss/colors')

export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Add Stone color palette
                stone: colors.stone,
                // Add Olive custom colors
                olive: {
                    600: '#6B8E23',
                    700: '#556B2F',
                    800: '#3d4d21',
                },
                // Retro Earth Theme (Windows 3.11)
                'desktop': 'var(--color-bg-desktop)',
                'window': 'var(--color-bg-window)',
                'window-border': 'var(--color-border-window)',
                'titlebar-active': 'var(--color-titlebar-active)',
                'titlebar-inactive': 'var(--color-titlebar-inactive)',
                'taskbar': 'var(--color-taskbar)',
                'btn': 'var(--color-button)',
                'btn-hover': 'var(--color-button-hover)',
                'accent': 'var(--color-accent)',
                'text-primary': 'var(--color-text-primary)',
                'text-inverse': 'var(--color-text-inverse)',
                'success': 'var(--color-success)',
                'warning': 'var(--color-warning)',
                'danger': 'var(--color-danger)',
            },
            fontFamily: {
                'pixel': ['"Press Start 2P"', 'Courier New', 'monospace'],
                'retro': ['"VT323"', 'Consolas', 'monospace'],
                'modern': ['Inter', 'Roboto', 'sans-serif'],
                'future': ['Orbitron', 'Exo 2', 'sans-serif'],
            },
            boxShadow: {
                'retro-outset': '2px 2px 0 #2F2F2F, -2px -2px 0 #FFFFFF',
                'retro-inset': 'inset 2px 2px 0 #2F2F2F, inset -2px -2px 0 #FFFFFF',
                'modern': '0 4px 6px rgba(0,0,0,0.1)',
                'space-glow': '0 0 10px #8B5CF6, 0 0 20px #8B5CF6',
            },
        },
    },
    plugins: [],
}
