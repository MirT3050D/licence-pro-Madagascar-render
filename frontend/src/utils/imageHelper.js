/**
 * Helper utility to handle Product images, specifically Google Drive shared links,
 * direct CDN links, and local backend media paths.
 */

export function extractGoogleDriveId(url) {
  if (!url || typeof url !== 'string') return null
  const trimmed = url.trim()

  // Match /file/d/FILE_ID
  const matchFileD = trimmed.match(/\/file\/d\/([a-zA-Z0-9_-]+)/)
  if (matchFileD && matchFileD[1]) {
    return matchFileD[1]
  }

  // Match ?id=FILE_ID or &id=FILE_ID
  const matchId = trimmed.match(/[?&]id=([a-zA-Z0-9_-]+)/)
  if (matchId && matchId[1]) {
    return matchId[1]
  }

  // Match /d/FILE_ID
  const matchD = trimmed.match(/\/d\/([a-zA-Z0-9_-]+)/)
  if (matchD && matchD[1]) {
    return matchD[1]
  }

  return null
}

export function isGoogleDriveUrl(url) {
  if (!url || typeof url !== 'string') return false
  const trimmed = url.trim()
  return (
    trimmed.includes('drive.google.com') ||
    trimmed.includes('docs.google.com') ||
    trimmed.includes('googleusercontent.com') ||
    !!extractGoogleDriveId(trimmed)
  )
}

export function getGoogleDriveViewerUrl(url) {
  const fileId = extractGoogleDriveId(url)
  if (fileId) {
    return `https://drive.google.com/file/d/${fileId}/view`
  }
  return url
}

export function resolveImageUrl(url) {
  if (!url || typeof url !== 'string') return ''
  const trimmed = url.trim()
  if (!trimmed) return ''

  // 1. Google Drive direct CDN
  const driveId = extractGoogleDriveId(trimmed)
  if (driveId) {
    return `https://lh3.googleusercontent.com/d/${driveId}`
  }

  // 2. Direct web URL or base64 data URI
  if (
    trimmed.startsWith('http://') ||
    trimmed.startsWith('https://') ||
    trimmed.startsWith('data:') ||
    trimmed.startsWith('blob:')
  ) {
    return trimmed
  }

  // 3. Relative backend media URL
  const apiBase = (typeof import.meta !== 'undefined' && import.meta?.env?.VITE_API_URL) || ''
  const host = apiBase.replace(/\/api\/?$/, '')
  return `${host}${trimmed.startsWith('/') ? '' : '/'}${trimmed}`
}

export function getGoogleDriveThumbnailFallback(url) {
  const driveId = extractGoogleDriveId(url)
  if (driveId) {
    return `https://drive.google.com/thumbnail?id=${driveId}&sz=w800`
  }
  return resolveImageUrl(url)
}
