# ConektaBots Frontend

Next.js 15 frontend for ConektaBots - Professional Telegram Bot Automation Platform.

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:3000

### Environment Variables

Copy `.env.local.example` to `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_PATH=/api/v1
```

## Project Structure

```
frontend/
├── app/                 # Next.js App Router
│   ├── (auth)/         # Auth routes (login, signup)
│   ├── (dashboard)/    # Protected dashboard routes
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Landing page
│   └── globals.css     # Global styles
├── lib/                # Utilities
│   ├── api.ts          # Axios wrapper with JWT interceptor
│   ├── auth.ts         # Token management
│   ├── constants.ts    # App constants & endpoints
│   └── types.ts        # TypeScript types
├── hooks/              # React hooks
│   └── useAuth.ts      # Authentication store (Zustand)
├── middleware.ts       # Protected routes middleware
├── next.config.js      # Next.js config
├── tailwind.config.js  # Tailwind CSS config
└── package.json
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - TypeScript type checking

## Technologies

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client with JWT auto-refresh
- **Zustand** - State management
- **React Hot Toast** - Toast notifications

## Architecture

### Authentication Flow
1. User login/signup
2. Backend returns JWT tokens (access + refresh)
3. Tokens stored in localStorage (access) + sessionStorage (user data)
4. Axios interceptor adds token to all requests
5. On 401, auto-refresh with refresh token
6. Failed refresh redirects to login

### Protected Routes
- Middleware checks for `auth_token` cookie
- Dashboard routes require authentication
- Unauthenticated users redirect to login

## Next Steps

- Task B1: Login/Signup pages with form validation
- Task B2: User profile & settings
- Task C1: Dashboard layout & bot management
- Task C2: Real-time features (WebSocket)

## Notes

- All API calls use environment-based URL
- JWT tokens automatically refreshed on 401
- Multi-tenant support via tenant_id header
- RBAC enforcement (owner, admin, editor, viewer)
