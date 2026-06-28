import { ArrowRight } from 'lucide-react'
import { useLanguage } from '../../hooks/useLanguage'

export function NextStepsPanel({ steps }) {
  const { t } = useLanguage()
  if (!steps?.length) return null
  return (
    <div className="bg-amber-50 border border-amber-100 rounded-xl p-4">
      <div className="flex items-center gap-2 text-amber-700 font-semibold text-sm mb-3">
        <ArrowRight size={16} /> {t('nextSteps')}
      </div>
      <ol className="space-y-1.5">
        {steps.map((step, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
            <span className="font-bold text-amber-600 min-w-[1.2rem]">{i + 1}.</span> {step}
          </li>
        ))}
      </ol>
    </div>
  )
}
