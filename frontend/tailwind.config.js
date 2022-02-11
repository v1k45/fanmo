const colors = require('tailwindcss/colors');
const defaultTheme = require('tailwindcss/defaultTheme');

const fontFamily = { ...defaultTheme.fontFamily };
delete fontFamily.serif;
fontFamily.sans.unshift('Quicksand');

const lightTheme = require('daisyui/colors/themes')['[data-theme=light]'];

module.exports = {
  content: [
    './components/**/*.{js,vue,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './plugins/**/*.{js,ts}'
  ],

  corePlugins: {
    container: false
  },

  plugins: [
    require('daisyui'),
    require('@tailwindcss/aspect-ratio'),
    require('tailwind-bootstrap-grid')({
      gridGutters: {
        0: 0,
        1: '.25rem',
        2: '.5rem',
        3: '1rem',
        4: '1.5rem',
        5: '3rem'
      },
      containerMaxWidths: {
        xl: '1280px',
        '2xl': '1280px'
      }
    })
  ],

  theme: {
    fontFamily,
    extend: {
      spacing: {
        em: '1em'
      },
      textColor: {
        title: colors.black,
        body: colors.gray['700']
      },
      colors: {
        inherit: 'inherit',
        'fm-primary': { DEFAULT: colors.indigo['500'], ...colors.indigo },
        'fm-success': { DEFAULT: colors.lime['500'], ...colors.lime },
        'fm-info': { DEFAULT: colors.blue['500'], ...colors.blue },
        'fm-warning': { DEFAULT: colors.yellow['500'], ...colors.yellow },
        'fm-error': { DEFAULT: colors.rose['500'], ...colors.rose }
      },
      fontFamily: {
        title: ['Yrsa', 'serif'],
        body: ['"Work Sans"', 'sans-serif']
      }
    }
  },

  daisyui: {
    styled: true,
    themes: [
      {
        brand: {
          ...lightTheme,
          primary: '#06f',
          'primary-focus': '#0052cc'
        }
      }
    ],
    base: false,
    utils: true,
    logs: true,
    rtl: false
  }
};
