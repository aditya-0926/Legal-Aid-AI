export const formatDistance = (km) =>
  km < 1 ? `${Math.round(km * 1000)}m` : `${km.toFixed(1)}km`

export const formatConfidence = (score) =>
  `${Math.round(score * 100)}%`

export const truncate = (str, n = 120) =>
  str.length > n ? str.slice(0, n) + '...' : str
