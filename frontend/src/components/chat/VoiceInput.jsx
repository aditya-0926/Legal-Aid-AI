import { Mic, MicOff } from 'lucide-react'
import { useVoice } from '../../hooks/useVoice'
import { useLanguage } from '../../hooks/useLanguage'

export function VoiceInput({ onTranscript }) {
  const { isListening, startListening, stopListening, isSupported } = useVoice()
  const { t } = useLanguage()

  if (!isSupported) return null

  const handleToggle = async () => {
    if (isListening) {
      const text = await stopListening()
      if (text) onTranscript(text)
    } else {
      await startListening()
    }
  }

  return (
    <button
      onClick={handleToggle}
      title={t('voiceInput')}
      className={`p-2 rounded-lg transition-all flex-shrink-0 ${
        isListening
          ? 'bg-red-100 text-red-600 animate-pulse ring-2 ring-red-300'
          : 'text-gray-400 hover:text-primary hover:bg-blue-50 dark:hover:bg-gray-700'
      }`}
    >
      {isListening ? <MicOff size={17} /> : <Mic size={17} />}
    </button>
  )
}
