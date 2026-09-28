// Helper utility for provenance badges, colors and icons
export function getProvenanceStyle(label) {
  const l = (label || '').toLowerCase().trim()
  if (l.includes('facebook') || l.includes('fb')) {
    return {
      bg: 'rgba(24, 119, 242, 0.16)',
      text: '#3b82f6',
      border: 'rgba(59, 130, 246, 0.35)',
      dot: '#3b82f6',
      emoji: '📘'
    }
  }
  if (l.includes('whatsapp') || l.includes('wa')) {
    return {
      bg: 'rgba(37, 211, 102, 0.16)',
      text: '#25d366',
      border: 'rgba(37, 211, 102, 0.35)',
      dot: '#25d366',
      emoji: '💬'
    }
  }
  if (l.includes('tiktok')) {
    return {
      bg: 'rgba(254, 44, 85, 0.16)',
      text: '#fe2c55',
      border: 'rgba(254, 44, 85, 0.35)',
      dot: '#fe2c55',
      emoji: '🎵'
    }
  }
  if (l.includes('insta')) {
    return {
      bg: 'rgba(225, 48, 108, 0.16)',
      text: '#e1306c',
      border: 'rgba(225, 48, 108, 0.35)',
      dot: '#e1306c',
      emoji: '📸'
    }
  }
  if (l.includes('linkedin')) {
    return {
      bg: 'rgba(10, 102, 194, 0.16)',
      text: '#0a66c2',
      border: 'rgba(10, 102, 194, 0.35)',
      dot: '#0a66c2',
      emoji: '💼'
    }
  }
  if (l.includes('site') || l.includes('web') || l.includes('google')) {
    return {
      bg: 'rgba(0, 210, 255, 0.16)',
      text: '#00d2ff',
      border: 'rgba(0, 210, 255, 0.35)',
      dot: '#00d2ff',
      emoji: '🌐'
    }
  }
  if (l.includes('bouche') || l.includes('recommandation') || l.includes('ami')) {
    return {
      bg: 'rgba(245, 158, 11, 0.16)',
      text: '#f59e0b',
      border: 'rgba(245, 158, 11, 0.35)',
      dot: '#f59e0b',
      emoji: '🤝'
    }
  }
  if (l.includes('appel') || l.includes('phone') || l.includes('tel')) {
    return {
      bg: 'rgba(16, 185, 129, 0.16)',
      text: '#10b981',
      border: 'rgba(16, 185, 129, 0.35)',
      dot: '#10b981',
      emoji: '📞'
    }
  }
  if (l.includes('direct') || l.includes('boutique') || l.includes('magasin')) {
    return {
      bg: 'rgba(168, 85, 247, 0.16)',
      text: '#a855f7',
      border: 'rgba(168, 85, 247, 0.35)',
      dot: '#a855f7',
      emoji: '🏬'
    }
  }
  return {
    bg: 'rgba(148, 163, 184, 0.16)',
    text: '#94a3b8',
    border: 'rgba(148, 163, 184, 0.35)',
    dot: '#94a3b8',
    emoji: '🏷️'
  }
}
