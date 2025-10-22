import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: false, // Skip DTS for now due to workspace dependency issues
  clean: true,
  external: [
    '@atproto/api',
    '@atproto/common',
    '@atproto/crypto',
    '@atproto/lexicon',
    '@atproto/syntax',
    '@atproto/xrpc',
    '@atproto-labs/did-resolver',
    '@atproto-labs/handle-resolver-node',
    '@atproto-labs/identity-resolver',
    'zod',
    'ajv',
    'ajv-formats'
  ]
})

