import { Scale, Moon, Sun, Upload } from 'lucide-react'
import { Link } from 'react-router-dom'
import { LanguageSelector } from './LanguageSelector'
import { useLanguage } from '../../hooks/useLanguage'
import { useChatStore } from '../../store/chatStore'
import { useEffect } from 'react'

export function Navbar() {
  const { t } = useLanguage()
  const { isDark, toggleDark } = useChatStore()

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDark)
  }, [isDark])

  return (
    <nav className="sticky top-0 z-40 bg-primary dark:bg-gray-900 shadow-md border-b border-primary-dark dark:border-gray-700">
      <div className="max-w-4xl mx-auto px-4 h-14 flex items-center justify-between gap-3">
        <Link to="/" className="flex items-center gap-2 text-white min-w-0">
          <Scale size={20} className="flex-shrink-0" />
          <span className="font-display font-bold text-base truncate">{t('freeLegalHelp')}</span>
        </Link>

        <div className="flex items-center gap-2">
          <LanguageSelector />
          <Link
            to="/upload"
            className="text-white/70 hover:text-white p-1.5 rounded transition-colors"
            title="Upload a law PDF"
          >
            <Upload size={16} />
          </Link>
          <button
            onClick={toggleDark}
            className="text-white/70 hover:text-white p-1.5 rounded transition-colors"
            title="Toggle dark mode"
          >
            {isDark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </div>
      </div>
    </nav>
  )
}
