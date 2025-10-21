# FundRhiz Web App

Next.js 15 application for FundRhiz - relationship-driven fundraising.

## Features

- 🔐 **Authentication** - Secure login and session management
- 📊 **Dashboard** - Trust metrics and network visualization
- 🔍 **Graph Explorer** - Interactive relationship graph
- 🤝 **Intro Requests** - Request and manage warm introductions
- 👥 **Network** - View and manage connections
- 🎯 **Settings** - Privacy controls and preferences

## Tech Stack

- **Next.js 15** with App Router
- **React 19**
- **TypeScript**
- **Tailwind CSS** for styling
- **React Query** for data fetching
- **Zustand** for state management
- **Rhiz Protocol** TypeScript SDK

## Getting Started

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Open http://localhost:3000
```

## Project Structure

```
src/
├── app/              # Next.js App Router pages
│   ├── (auth)/      # Auth-required routes
│   ├── (public)/    # Public routes
│   └── layout.tsx   # Root layout
├── components/       # React components
│   ├── ui/          # Base UI components
│   ├── graph/       # Graph visualizations
│   └── forms/       # Form components
├── lib/             # Utilities and helpers
│   ├── api.ts       # API client
│   ├── auth.ts      # Auth helpers
│   └── utils.ts     # General utilities
└── stores/          # Zustand stores
```

## Environment Variables

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=FundRhiz
```

## Development

```bash
# Type checking
pnpm typecheck

# Linting
pnpm lint

# Testing
pnpm test

# Build for production
pnpm build
```

## Deployment

```bash
# Build
pnpm build

# Start production server
pnpm start
```

Optimized for deployment on Vercel, but works with any Node.js hosting.

## License

MIT

