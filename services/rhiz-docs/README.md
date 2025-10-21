# Rhiz Protocol Documentation

Documentation site built with Docusaurus.

## Installation

```bash
pnpm install
```

## Local Development

```bash
pnpm start
```

This starts a local development server at `http://localhost:3000`.

## Build

```bash
pnpm build
```

This command generates static content into the `build` directory.

## Deployment

```bash
pnpm deploy
```

Deploys to GitHub Pages (or configure for your hosting platform).

## Writing Documentation

### Create a New Doc

Add a new markdown file to `docs/`:

```bash
docs/
  my-new-doc.md
```

Add it to `sidebars.js`:

```js
{
  type: 'doc',
  id: 'my-new-doc',
}
```

### API Documentation

API docs are in `docs/api/`. Use code examples with syntax highlighting:

```markdown
\```typescript
const client = new RhizClient({ apiUrl: '...' });
\```
```

### Live Reload

Changes are reflected instantly in the browser during development.

## License

MIT

