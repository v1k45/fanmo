const colors = require('tailwindcss/colors');
const defaultTheme = require('tailwindcss/defaultTheme');

const fontFamily = { ...defaultTheme.fontFamily };
delete fontFamily.serif;
fontFamily.sans.unshift('Quicksand');

const lightTheme = require('daisyui/colors/themes')['[data-theme=light]'];

const brandColors = {
  primary: {
    DEFAULT: '#6B68F9',
    100: '#E1E1FE',
    200: '#C4C3FE',
    300: '#A6A4FD',
    400: '#908DFB',
    500: '#6B68F9',
    600: '#4E4CD6',
    700: '#3634B3',
    800: '#222190',
    900: '#151377'
  },
  success: {
    DEFAULT: '#9DCE0A',
    50: colors.lime['50'],
    100: '#F5FCCC',
    200: '#E9FA9A',
    300: '#D5F067',
    400: '#BDE140',
    500: '#9DCE0A',
    600: '#82B107',
    700: '#699405',
    800: '#517703',
    900: '#406201'
  },
  info: {
    DEFAULT: '#028DFF',
    50: colors.blue['50'],
    100: '#CCF3FF',
    200: '#99E1FF',
    300: '#67CBFF',
    400: '#41B3FF',
    500: '#028DFF',
    600: '#016DDB',
    700: '#0151B7',
    800: '#003993',
    900: '#00287A'
  },
  warning: {
    DEFAULT: '#FFBB00',
    50: colors.yellow['50'],
    100: '#FFF7CC',
    200: '#FFEC99',
    300: '#FFDE66',
    400: '#FFD13F',
    500: '#FFBB00',
    600: '#DB9A00',
    700: '#B77C00',
    800: '#936000',
    900: '#7A4C00'
  },
  error: {
    DEFAULT: '#FF5647',
    50: colors.rose['50'],
    100: '#FFE9DA',
    200: '#FFCDB5',
    300: '#FFAB90',
    400: '#FF8B75',
    500: '#FF5647',
    600: '#DB3333',
    700: '#B7232F',
    800: '#93162B',
    900: '#7A0D28'
  },
  gray: {
    DEFAULT: '#B0B2C1',
    50: '#F9F9FA',
    100: '#EDEDF1',
    200: '#E0E0E6',
    300: '#D1D2DB',
    400: '#C2C3CF',
    500: '#B0B2C1',
    600: '#9D9FAD',
    700: '#878895',
    800: '#6A6C75',
    900: '#3E3F45',
    darkest: '#1D1D20'
  }
};

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
    require('@tailwindcss/forms'),
    require('tailwind-animatecss'),
    require('@tailwindcss/line-clamp'),
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
        body: colors.gray['800']
      },
      colors: {
        inherit: 'inherit',
        // TODO: update this eventually
        'fm-primary': { DEFAULT: colors.indigo['500'], ...colors.indigo },
        'fm-success': { DEFAULT: colors.emerald['500'], ...colors.emerald }, // brandColors.success,
        'fm-info': brandColors.info,
        'fm-warning': { DEFAULT: colors.amber['500'], ...colors.amber }, // brandColors.warning,
        'fm-error': brandColors.error
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
