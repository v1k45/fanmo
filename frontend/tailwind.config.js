const defaultTheme = require('tailwindcss/defaultTheme');

const fontFamily = { ...defaultTheme.fontFamily };
delete fontFamily.serif;
fontFamily.sans.unshift('Quicksand');

const lightTheme = require('daisyui/colors/themes')['[data-theme=light]'];

module.exports = {
  important: '#app',

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
      }
      // containerMaxWidths: { sm: '540px', md: '720px', lg: '960px', xl: '1140px' }
    })
  ],

  theme: {
    fontFamily,
    extend: {
      colors: {
        inherit: 'inherit'
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
