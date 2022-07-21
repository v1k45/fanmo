<template>
<div
  v-loading="showGlobalLoader"
  class="fm-layout fm-layout--default bg-gray-50"
  :class="{
    'fm-layout--with-sidebar': sidebar && $auth.loggedIn,
    'fm-layout--with-header-banner': onboarding.isPending
  }">
  <!-- header start -->
  <!-- TODO: always show for marketing pages and remove bottom pane -->
  <header class="fm-layout__header z-20 py-2 bg-white shadow-sm" :class="{ 'hidden md:block': $auth.loggedIn }">
    <div class="max-w-[1390px] container-fluid flex items-center">
      <breakpoint-helper></breakpoint-helper>

      <nuxt-link to="/" class="mr-auto">
        <logo class="h-6"></logo>
      </nuxt-link>

      <nav>
        <button class="p-3 md:hidden text-fm-primary" @click="isNavVisibleMobile = !isNavVisibleMobile;">
          <div class="sr-only">Menu</div>
          <icon-menu v-if="!isNavVisibleMobile"></icon-menu>
          <icon-x v-else></icon-x>
        </button>
        <ul :class="{
          'text-sm absolute left-0 top-full w-full bg-white space-y-6 p-6': true,
          'md:flex md:items-center md:space-x-12 md:static md:w-auto md:p-0 md:space-y-0': true,
          'hidden': !isNavVisibleMobile,
        }">
          <template v-if="$auth.loggedIn">
            <template v-if="marketing">
              <li><nuxt-link class="unstyled" to="/pricing">Pricing</nuxt-link></li>
              <li><nuxt-link class="unstyled" to="/pricing#comparison">Comparison</nuxt-link></li>
            </template>
            <li>
              <layout-navigation type="hamburger"></layout-navigation>
            </li>
          </template>
          <template v-else>
            <li><nuxt-link class="unstyled" to="/pricing">Pricing</nuxt-link></li>
            <li><nuxt-link class="unstyled" to="/pricing#comparison">Comparison</nuxt-link></li>
            <li><nuxt-link class="unstyled" to="/login">Login</nuxt-link></li>
            <li>
              <nuxt-link
                to="/register"
                class="unstyled inline-block px-8 py-3 transition-colors rounded-full bg-fm-primary-100 hover:bg-fm-primary-500 hover:text-white">
                Sign up
              </nuxt-link>
            </li>
          </template>
        </ul>
      </nav>
    </div>
  </header>

  <!-- onboarding banner start -->
  <fm-alert v-if="onboarding.isPending" :show-icon="false" class="fm-layout__banner !rounded-none z-[15]">
    <div class="sm:container flex items-center relative text-sm sm:text-base">
      <div class="mr-3 hidden sm:block"><icon-info></icon-info></div>
      <div class="mr-auto">
        <span class="hidden lg:inline">{{ onboarding.text }}</span>
        <span class="lg:hidden">{{ onboarding.smallText }}</span>
      </div>
      <div class="absolute right-0 sm:right-4 top-[-7px] hidden sm:block">
        <fm-button type="success" @click="continueOnboarding">Finish setup</fm-button>
      </div>
      <fm-button class="sm:hidden" size="sm" type="success" @click="continueOnboarding">Finish setup</fm-button>
    </div>
  </fm-alert>
  <!-- onboarding banner end -->

  <!-- header end -->

  <div class="fm-layout__content">
    <div v-if="sidebar && $auth.loggedIn" class="fm-layout__sidebar">
      <layout-navigation class="m-4 mt-12" type="sidebar"></layout-navigation>
    </div>

    <slot v-if="custom"></slot>
    <template v-else>
      <main v-if="container" class="container py-8 flex-grow">
        <Nuxt></Nuxt>
      </main>
      <Nuxt v-else></Nuxt>
    </template>
  </div>

  <!-- footer start -->
  <layout-footer class="fm-layout__footer hidden md:block mt-auto"></layout-footer>
  <!-- footer end -->

  <div v-if="$auth.loggedIn" class="fm-layout__bottom-pane z-20 py-2 bg-white shadow border-t">
    <layout-navigation type="bottom-pane"></layout-navigation>
  </div>
</div>
</template>

<script>
import { Menu as IconMenu, X as IconX } from 'lucide-vue';
import { mapState } from 'vuex';
import { skipOnboarding } from '~/utils';

export default {
  components: {
    IconMenu,
    IconX
  },
  props: {
    container: { type: Boolean, default: true },
    sidebar: { type: Boolean, default: false },
    custom: { type: Boolean, default: false },
    marketing: { type: Boolean, default: false }
  },
  data() {
    return {
      isNavVisibleMobile: false,
      currentYear: new Date().getFullYear()
    };
  },
  computed: {
    ...mapState('ui', ['showGlobalLoader']),

    /* eslint-disable camelcase */
    onboarding() {
      const { loggedIn, user } = this.$auth;
      if (!loggedIn) return { isPending: false };
      const isPending = user.onboarding.status === 'in_progress';

      let text, smallText;
      const { email_verification, payment_setup } = user.onboarding.checklist;
      if (user.is_creator) { // creator
        if (!payment_setup) {
          text = 'Finish your account setup now to start accepting payments from your supporters.';
          smallText = 'Finish your account setup.';
        }
      } else { // supporter
        // eslint-disable-next-line no-lonely-if
        if (!email_verification) {
          text = 'Verify your email now to unlock all features!';
          smallText = 'Verify your email.';
        }
      }
      return {
        isPending,
        text,
        smallText
      };
    }
  },
  methods: {
    continueOnboarding() {
      skipOnboarding.unset(this.$auth.user.username);
      location.reload();
    }
  }
};
</script>
<style lang="scss">
$header-height: 60px;
$banner-height: 54px;
$top-offset-with-banner: $header-height + $banner-height;

.fm-layout {
  @apply grid;
}

.fm-layout--default {
  @apply min-h-screen max-w-full;
  grid-template-areas:
    'header'
    'banner'
    'content'
    'footer'
    'bottom-pane';
  grid-template-rows: auto auto minmax(0, 1fr) auto auto;
  grid-template-columns: minmax(0, 1fr);
}
.fm-layout--with-sidebar {
  .fm-layout__content {
    @apply flex mx-auto;
    width: 100%;
    max-width: 250px + 1140px;
  }
  .fm-layout__sidebar {
    @apply flex-shrink-0 overflow-auto sticky mr-4 hidden lg:block;
    width: 250px;
    height: calc(100vh - $header-height);
    top: $header-height;
    + * {
      flex-grow: 1;
      min-width: 0;
    }
  }
}
.fm-layout--with-minimal-branding {}

.fm-layout--with-bottom-pane {}


.fm-layout__header {
  grid-area: header;
  height: $header-height;
  @apply sticky top-0;
}
.fm-layout__banner {
  @apply sticky top-0;
  height: $banner-height;
  @screen md {
    top: $header-height;
  }
}
.fm-layout__content {
  grid-area: content;
}
.fm-layout__footer {
  grid-area: footer;
}
.fm-layout__bottom-pane {
  grid-area: bottom-pane;
  height: 78px;
  @apply sticky bottom-0 md:hidden;
}

.fm-layout--with-header-banner {
  .fm-layout__sidebar {
    height: calc(100vh - $top-offset-with-banner);
    top: $top-offset-with-banner;
  }
}

// TODO: delete this comment after all the pages are implemented
/*
  For creator:
    Dashboard
    Members
      List view
      Tier management
    Donations
      List view
      Settings (thank you message etc.)
    Payment history
    Profile
    Settings

    Feed (Supporter dashboard)
    My memberships
    My donations
  For supporter
    Dashboard
    My memberships
    My donations
    My account
*/

</style>
