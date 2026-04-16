import { NextResponse } from 'next/server'

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export function middleware() {
  // Client-side auth checks will handle the redirects in useEffect
  // This middleware is just a safety net for basic routing
  return NextResponse.next()
}

export const config = {
  matcher: ['/dashboard/:path*', '/login', '/signup'],
}
