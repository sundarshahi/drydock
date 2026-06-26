import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

const config: Config = {
  title: 'Drydock',
  tagline: 'An idea-to-launch product team for Claude Code',
  favicon: 'img/favicon.ico',

  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Production URL — Cloudflare Pages custom subdomain.
  url: 'https://drydock.sundarshahithakuri.com.np',
  baseUrl: '/',

  organizationName: 'sundarshahi',
  projectName: 'drydock',

  onBrokenLinks: 'throw',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'docs',
          editUrl: 'https://github.com/sundarshahi/drydock/tree/main/website/',
        },
        blog: false, // Drydock's blog lives on the portfolio; this is docs-only.
        theme: {
          customCss: './src/css/custom.css',
        },
        sitemap: {
          changefreq: 'weekly',
          priority: 0.5,
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    metadata: [
      {name: 'keywords', content: 'claude code, plugin, ai agents, multi-agent, devops, security, owasp, vapt, compliance, ci-cd, idea to launch'},
    ],
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Drydock',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'docsSidebar',
          position: 'left',
          label: 'Docs',
        },
        {to: '/docs/getting-started/installation', label: 'Install', position: 'left'},
        {to: '/docs/agents/overview', label: 'Agents', position: 'left'},
        {
          href: 'https://github.com/sundarshahi/drydock',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Introduction', to: '/docs/intro'},
            {label: 'Installation', to: '/docs/getting-started/installation'},
            {label: 'How it works', to: '/docs/concepts/how-it-works'},
            {label: 'The 19 agents', to: '/docs/agents/overview'},
          ],
        },
        {
          title: 'Project',
          items: [
            {label: 'GitHub', href: 'https://github.com/sundarshahi/drydock'},
            {label: 'Releases', href: 'https://github.com/sundarshahi/drydock/releases'},
            {label: 'Changelog', to: '/docs/changelog'},
          ],
        },
        {
          title: 'More',
          items: [
            {label: 'Blog post', href: 'https://sundarshahithakuri.com.np/blog/drydock-agent-product-team'},
            {label: 'sundarshahithakuri.com.np', href: 'https://sundarshahithakuri.com.np'},
          ],
        },
      ],
      copyright: `Drydock is open-source under the MIT License. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.oneLight,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'json', 'yaml'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
