// sidebars.js

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    {
      type: 'doc',
      id: 'what-is-adapty',
      label: 'What is Adapty?',
    },
    {
      type: 'category',
      label: 'Migrate to Adapty',
      link: {
        type: 'doc',
        id: 'migrate-to-adapty-from-another-solutions',
      },
      collapsible: true,
      collapsed: false,
      items: [
        {
          type: 'doc',
          id: 'migration-from-revenuecat',
          label: 'Migration from RevenueCat',
        },
      ],
    },
  ],
};

module.exports = sidebars;
