import { useLanguage } from '../../hooks/useLanguage'
import { LANGUAGES } from '../../utils/constants'

export function LanguageSelector() {
  const { language, setLanguage } = useLanguage()
  return (
    <div className="flex gap-1">
      {LANGUAGES.map((l) => (
        <button
          key={l.code}
          onClick={() => setLanguage(l.code)}
          className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
            language === l.code ? 'bg-white text-primary' : 'text-white/80 hover:text-white hover:bg-white/10'
          }`}
        >
          {l.nativeLabel}
        </button>
      ))}
    </div>
  )
}
