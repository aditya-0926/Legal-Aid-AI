import { MapPin, Phone } from 'lucide-react'
import { useLanguage } from '../../hooks/useLanguage'
import { formatDistance } from '../../utils/formatters'

export function LegalCenterMap({ centers }) {
  const { t } = useLanguage()
  if (!centers?.length) return null
  return (
    <div className="border border-gray-100 rounded-xl p-4">
      <div className="flex items-center gap-2 text-gray-700 font-semibold text-sm mb-3">
        <MapPin size={16} className="text-red-500" /> {t('nearbyCenters')}
      </div>
      <div className="space-y-3">
        {centers.map((c, i) => (
          <div key={i} className="flex items-start justify-between gap-2">
            <div>
              <p className="text-sm font-medium text-gray-800">{c.name}</p>
              <p className="text-xs text-gray-500">{c.address}</p>
              <a href={`tel:${c.phone}`} className="text-xs text-primary flex items-center gap-1 mt-0.5">
                <Phone size={10} /> {c.phone}
              </a>
            </div>
            <span className="text-xs text-gray-400 whitespace-nowrap">{formatDistance(c.distance_km)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
