import { useLanguageStore } from '../store/languageStore'
import { t } from '../utils/i18n'

export function useLanguage() {
  const { language, setLanguage } = useLanguageStore()
  const translate = (key) => t(language, key)
  return { language, setLanguage, t: translate }
}
