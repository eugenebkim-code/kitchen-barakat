// Helper to get backend API base URL
let rawUrl = import.meta.env.VITE_API_URL || ''
if (rawUrl.endsWith('/')) {
  rawUrl = rawUrl.slice(0, -1)
}
export const API_BASE = rawUrl

