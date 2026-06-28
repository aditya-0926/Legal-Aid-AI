import { useState, useEffect } from 'react'
import { getUserLocation } from '../services/geolocation'

export function useLocation() {
  const [coords, setCoords] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    getUserLocation()
      .then(setCoords)
      .catch((e) => setError(e.message))
  }, [])

  return { coords, error }
}
