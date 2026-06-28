import { create } from 'zustand'

export const useChatStore = create((set) => ({
  messages: [],
  isLoading: false,
  sessionId: null,
  isDark: false,

  addUserMessage: (text) =>
    set((s) => ({
      messages: [...s.messages, { role: 'user', content: text, id: Date.now() }],
    })),

  addAssistantMessage: (response) =>
    set((s) => ({
      messages: [...s.messages, { role: 'assistant', content: response, id: Date.now() }],
      sessionId: response.session_id,
      isLoading: false,
    })),

  setLoading: (val) => set({ isLoading: val }),
  clearChat: () => set({ messages: [], sessionId: null }),
  toggleDark: () => set((s) => ({ isDark: !s.isDark })),
}))
