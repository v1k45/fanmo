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
    titleTemplate: titleChunk => titleChunk ? `${titleChunk} | Fanmo` : 'Fanmo',
    htmlAttrs: {
      lang: 'en',
      'data-theme': 'brand'
    },
    bodyAttrs: {
      id: 'app'
    },
    meta: [
      { charset: 'utf-8' },
      // https://stackoverflow.com/questions/44679794/position-fixed-on-chrome-mobile-causing-element-to-move-on-scroll-up-down
      { name: 'viewport', content: 'height=device-height, width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=1.0, user-scalable=no, target-densitydpi=device-dpi' },
      { hid: 'description', name: 'description', content: '' },
      { name: 'format-detection', content: 'telephone=no' }
    ],
    link: []
  },

  // Global CSS: https://go.nuxtjs.dev/config-css
  css: [
    '@/assets/styles/index.scss'
  ],

  // Plugins to run before rendering page: https://go.nuxtjs.dev/config-plugins
  plugins: [
    '~/components/fm/init.js',
    '~/plugins/axios',
    '~/plugins/directives.client.js'
  ],

  // Auto import components: https://go.nuxtjs.dev/config-components
  components: [
    {
      path: '~/components',
      ignore: ['./fm/*/**.{vue,js}']
    }
  ],

  // Modules for dev and build (recommended): https://go.nuxtjs.dev/config-modules
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    '@nuxtjs/eslint-module',
    // https://go.nuxtjs.dev/tailwindcss
    '@nuxt/postcss8',
    'lucide-vue/nuxt',
    '@nuxtjs/svg'
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
    redirect: {
      login: '/login',
      logout: '/',
      callback: '/auth/callback',
      home: '/auth/'
    },
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
      },
      google: {
        clientId: 'FANMO_SECRET_CHANGE_ME',
        responseType: 'code',
        grantType: 'authorization_code',
        codeChallengeMethod: '',
        endpoints: {
          token: '/api/auth/login/google/',
          userInfo: '/api/me/',
          logout: ''
        },
        // hack to make cookie auth look like jwt auth
        // makes nuxt-auth include Authorization: <type> <username> header instead of failing.
        // fuck nuxt-auth
        token: { property: 'username', type: 'google' },
        user: { property: false }
      },
      facebook: {
        clientId: 'FANMO_SECRET_CHANGE_ME',
        responseType: 'code',
        grantType: 'authorization_code',
        codeChallengeMethod: '',
        endpoints: {
          token: '/api/auth/login/facebook/',
          userInfo: '/api/me/',
          logout: ''
        },
        token: { property: 'username', type: 'facebook' },
        user: { property: false }
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
    middleware: [
      'auth',
      'router'
    ]
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
