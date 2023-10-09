import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

import tailwind from "@astrojs/tailwind";

// https://astro.build/config
export default defineConfig({
  base: '/docs',
  integrations: [starlight({
    title: 'Fanmo Help',
    logo: {
      replacesTitle: true,
      src: './src/assets/logo.svg'
    },
    customCss: [
      // Path to your Tailwind base styles:
      './src/tailwind.css',
    ],
    favicon: './favicon.png',
    sidebar: [
      {
        label: 'Getting Started',
        autogenerate: {
          directory: 'getting-started'
        }
      },
      {
        label: 'Memberships',
        autogenerate: {
          directory: 'memberships'
        }
      },
      {
        label: 'Fanmo Tips',
        autogenerate: {
          directory: 'tips'
        }
      },
      {
        label: 'Fanmo Posts',
        autogenerate: {
          directory: 'posts'
        }
      },
    ],
    head: [
      {
        // force light theme
        // only other way is to override layout, which is too much work
        tag: 'script',
        content: `localStorage.setItem("starlight-theme", "light");`
      }
    ],
  }), tailwind({
    applyBaseStyles: false,
  })]
});
