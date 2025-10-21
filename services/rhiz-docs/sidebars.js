/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting Started',
      items: ['getting-started/installation', 'getting-started/quickstart'],
    },
    {
      type: 'category',
      label: 'Protocol',
      items: [
        'protocol/overview',
        'protocol/relationships',
        'protocol/trust-metrics',
        'protocol/privacy',
      ],
    },
    {
      type: 'category',
      label: 'API Reference',
      items: [
        'api/overview',
        'api/graph',
        'api/entities',
        'api/analytics',
        'api/authentication',
      ],
    },
    {
      type: 'category',
      label: 'SDKs',
      items: ['sdks/typescript', 'sdks/python'],
    },
    {
      type: 'category',
      label: 'Guides',
      items: ['guides/local-development', 'guides/deployment'],
    },
  ],
};

export default sidebars;

