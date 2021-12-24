export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  server: {
    host: '0.0.0.0'
  },

  // Target: https://go.nuxtjs.dev/config-target
  target: 'static',

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    titleTemplate: titleChunk => titleChunk ? `${titleChunk} | fanmo` : 'fanmo',
    htmlAttrs: {
      lang: 'en',
      'data-theme': 'mod'
    },
    bodyAttrs: {
      id: 'app'
    },
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ],
    script: [
      { src: 'https://checkout.razorpay.com/v1/checkout.js' }
    ]
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    '@/assets/styles/index.scss'
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    '~/plugins/axios',
    '~/plugins/directives.client.js'
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: true,

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    '@nuxtjs/eslint-module',
    // https://go.nuxtjs.dev/tailwindcss
    '@nuxt/postcss8',
    'lucide-vue/nuxt'
  ],

  // Modules: https://go.nuxtjs.dev/config-modules
  modules: [
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    '@nuxtjs/auth-next'
  ],

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    proxy: true,
    credentials: true
  },

  auth: {
    strategies: {
      cookie: {
        endpoints: {
          // (optional) If set, we send a get request to this endpoint before login
          login: { url: '/api/auth/login/', method: 'post' },
          logout: { url: '/api/auth/logout/', method: 'post' },
          user: { url: '/api/me/', method: 'get', propertyName: '' }
        },
        user: {
          property: false
        }
      }
    }
  },

  proxy: {
    '/api/': {
      target: process.env.API_URL,
      secure: process.env.ENV === 'production',
      headers: {
        referer: process.env.API_URL
      }
    }
  },

  // Build Configuration: https://go.nuxtjs.dev/config-build
  generate: {
    dir: '/var/www/html'
  },

  router: {
    middleware: ['auth']
  },

  build: {
    postcss: {
      plugins: {
        tailwindcss: {},
        autoprefixer: {}
      }
    }
  }
};
