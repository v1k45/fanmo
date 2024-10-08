const config = {
  dev: {
    google: 'FANMO_SECRET_CHANGE_ME',
    facebook: 'FANMO_SECRET_CHANGE_ME',
    ogImage: 'https://dev.fanmo.in/ogimage.png',
    discord: 'FANMO_SECRET_CHANGE_ME'
  },
  prod: {
    google: 'FANMO_SECRET_CHANGE_ME',
    facebook: 'FANMO_SECRET_CHANGE_ME',
    ogImage: 'https://fanmo.in/ogimage.png',
    discord: 'FANMO_SECRET_CHANGE_ME'
  }
};

const envConfig = config[process.env.STAGE || 'dev'];

const seoValues = {
  title: 'Fanmo - Build a stable income from your passion',
  description: 'Fanmo is the simplest way to offer monthly memberships, accept tips and post member-only content. Create your Fanmo page today, it takes less than 5 minutes to get started.',
  keywords: 'fanmo, memberships, donations, tips, patreon alternative, buymeacoffee alternative, india, creators, supporters, low cost',
  image: envConfig.ogImage
};

export default {
  // Disable server-side rendering: https://go.nuxtjs.dev/ssr-mode
  ssr: false,

  modern: 'client',

  server: {
    host: '0.0.0.0'
  },

  publicRuntimeConfig: envConfig,

  // Target: https://go.nuxtjs.dev/config-target
  target: 'static',

  // Global page headers: https://go.nuxtjs.dev/config-head
  head: {
    // title has to be hardcoded because nuxt is pasting the function contents over to the component  https://github.com/nuxt/nuxt.js/issues/4457
    titleTemplate: titleChunk => titleChunk ? `${titleChunk} | Fanmo` : 'Fanmo - Build a stable income from your passion',
    htmlAttrs: {
      lang: 'en',
      'data-theme': 'brand'
    },
    bodyAttrs: {
      id: 'app'
    },
    /**
     * !!!!!!!!!!!!!!!! DO NOT CHANGE META SECTION WITHOUT DOUBLE CHECKING THE REGEX IN BACKEND !!!!!!!!!!!!!!!!!!!!
     */
    meta: [
      { charset: 'utf-8' },
      // https://stackoverflow.com/questions/44679794/position-fixed-on-chrome-mobile-causing-element-to-move-on-scroll-up-down
      { name: 'viewport', content: 'height=device-height, width=device-width, initial-scale=1.0, minimum-scale=1.0, maximum-scale=5.0' },
      { name: 'format-detection', content: 'telephone=no' },
      // seo
      { name: 'description', content: seoValues.description, hid: 'description' },
      { name: 'keywords', content: seoValues.keywords, hid: 'keywords' },
      // facebook
      { property: 'og:title', content: seoValues.title, hid: 'og:title' },
      { property: 'og:description', content: seoValues.description, hid: 'og:description' },
      { property: 'og:image', content: seoValues.image, hid: 'og:image' },
      { property: 'og:site_name', content: 'Fanmo', hid: 'og:site_name' },
      // twitter
      { name: 'twitter:card', content: 'summary_large_image', hid: 'twitter:card' },
      { name: 'twitter:title', content: seoValues.title, hid: 'twitter:title' },
      { name: 'twitter:description', content: seoValues.description, hid: 'twitter:description' },
      { name: 'twitter:image', content: seoValues.image, hid: 'twitter:image' },
      { name: 'twitter:site', content: '@getfanmo', hid: 'twitter:site' }
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
    '@nuxtjs/auth-next',
    '@nuxtjs/gtm'
  ],

  gtm: {
    id: 'G-S7RPVV0MPE'
  },

  // Axios module configuration: https://go.nuxtjs.dev/config-axios
  axios: {
    proxy: true,
    credentials: true
  },

  auth: {
    redirect: {
      login: '/login',
      logout: '/',
      callback: '/auth/callback/',
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
        clientId: envConfig.google,
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
        clientId: envConfig.facebook,
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
  },

  loadingIndicator: {
    name: 'circle',
    color: '#626be9',
    background: 'white'
  }
};
