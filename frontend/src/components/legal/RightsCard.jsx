import { ShieldCheck } from 'lucide-react'
import { useLanguage } from '../../hooks/useLanguage'

export function RightsCard({ rights }) {
  const { t } = useLanguage()
  if (!rights?.length) return null
  return (
    <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
      <div className="flex items-center gap-2 text-primary font-semibold text-sm mb-3">
        <ShieldCheck size={16} /> {t('yourRights')}
      </div>
      <ul className="space-y-1.5">
        {rights.map((r, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
            <span className="text-primary mt-0.5">•</span> {r}
          </li>
        ))}
      </ul>
    </div>
  )
}
