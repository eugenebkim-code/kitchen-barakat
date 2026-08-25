// Helper to get backend API base URL
let rawUrl = import.meta.env.VITE_API_URL || ''
if (rawUrl.endsWith('/')) {
  rawUrl = rawUrl.slice(0, -1)
}
export const API_BASE = rawUrl

// Resolves a possibly-relative image path (e.g. "/uploads/x.jpg") returned by
// the backend into an absolute URL. Frontend and backend live on different
// domains, so a bare relative path would otherwise resolve against the
// frontend's own origin. Already-absolute URLs (seeded Telegram file links,
// external images) are passed through unchanged.
export function resolveImageUrl(path) {
  if (!path) return ''
  if (/^https?:\/\//i.test(path)) return path
  return `${API_BASE}${path}`
}


