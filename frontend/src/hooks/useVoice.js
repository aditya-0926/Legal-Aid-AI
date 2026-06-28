import { useState } from 'react'
import { AudioRecorder } from '../services/whisper'
import { transcribeAudio } from '../services/api'
import { useLanguageStore } from '../store/languageStore'

export function useVoice() {
  const [isListening, setIsListening] = useState(false)
  const [recorder] = useState(() => new AudioRecorder())
  const { language } = useLanguageStore()
  const isSupported = typeof navigator !== 'undefined' && !!navigator.mediaDevices?.getUserMedia

  const startListening = async () => {
    setIsListening(true)
    try { await recorder.start() }
    catch (e) { setIsListening(false); throw e }
  }

  const stopListening = async () => {
    try {
      const base64 = await recorder.stop()
      setIsListening(false)
      const { text } = await transcribeAudio({ audio_base64: base64, language })
      return text
    } catch (e) {
      setIsListening(false)
      console.error('Transcription error:', e)
      return ''
    }
  }

  return { isListening, startListening, stopListening, isSupported }
}
