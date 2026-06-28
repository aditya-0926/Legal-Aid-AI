import { useChatStore } from '../store/chatStore'
import { useLanguageStore } from '../store/languageStore'
import { sendMessage } from '../services/api'
import { getUserLocation } from '../services/geolocation'

export function useChat() {
  const { addUserMessage, addAssistantMessage, setLoading, isLoading, messages } = useChatStore()
  const { language } = useLanguageStore()

  const sendQuery = async (message) => {
    if (isLoading) return
    addUserMessage(message)
    setLoading(true)

    let coords = null
    try { coords = await getUserLocation() } catch (_) {}

    // Build history from last 10 messages for context
    const history = messages.slice(-10).map((m) => ({
      role: m.role,
      content: m.role === 'user' ? m.content : (m.content?.answer ?? ''),
    }))

    try {
      const response = await sendMessage({
        message,
        language,
        history,
        latitude: coords?.latitude ?? null,
        longitude: coords?.longitude ?? null,
      })
      addAssistantMessage(response)
    } catch (err) {
      addAssistantMessage({
        session_id: 'error',
        domain: 'general',
        domain_confidence: 0,
        answer: `**Error:** ${err.message}`,
        rights_summary: [],
        next_steps: [],
        sources: [],
        nearby_centers: [],
        language,
        confidence: 0,
        isError: true,
      })
    }
  }

  return { sendQuery, isLoading }
}
