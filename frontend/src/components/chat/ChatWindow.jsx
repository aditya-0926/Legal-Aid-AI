import { useEffect, useRef, useState, useCallback } from 'react'
import { Send, Trash2 } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { useChat } from '../../hooks/useChat'
import { useLanguage } from '../../hooks/useLanguage'
import { MessageBubble } from './MessageBubble'
import { TypingIndicator } from './TypingIndicator'
import { VoiceInput } from './VoiceInput'
import { EXAMPLE_QUERIES } from '../../utils/constants'

export function ChatWindow() {
  const [input, setInput] = useState('')
  const { messages, isLoading, clearChat } = useChatStore()
  const { sendQuery } = useChat()
  const { language, t } = useLanguage()
  const bottomRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSend = useCallback(async () => {
    const msg = input.trim()
    if (!msg || isLoading) return
    setInput('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
    await sendQuery(msg)
  }, [input, isLoading, sendQuery])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleInput = (e) => {
    setInput(e.target.value)
    // Auto-grow textarea
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 140) + 'px'
  }

  const examples = EXAMPLE_QUERIES[language] ?? EXAMPLE_QUERIES.en

  return (
    <div className="flex flex-col h-full bg-surface dark:bg-gray-900">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-5">
        {messages.length === 0 ? (
          <div className="text-center pt-8 pb-4 space-y-6 max-w-xl mx-auto">
            <div className="space-y-2">
              <div className="text-4xl">⚖️</div>
              <h1 className="text-2xl font-display font-bold text-primary dark:text-blue-400">
                {t('freeLegalHelp')}
              </h1>
              <p className="text-gray-500 dark:text-gray-400 text-sm">{t('tagline')}</p>
            </div>

            <div className="space-y-2">
              <p className="text-xs text-gray-400 font-semibold uppercase tracking-widest">
                {t('tryExample')}
              </p>
              {examples.map((q, i) => (
                <button
                  key={i}
                  onClick={() => sendQuery(q)}
                  disabled={isLoading}
                  className="w-full text-left text-sm bg-white dark:bg-gray-800 border border-gray-200
                             dark:border-gray-700 rounded-xl px-4 py-3 text-gray-700 dark:text-gray-300
                             hover:border-primary hover:bg-blue-50 dark:hover:bg-gray-700
                             transition-all disabled:opacity-50"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white dark:bg-gray-800 border border-gray-100 dark:border-gray-700 rounded-2xl shadow-sm">
                  <TypingIndicator />
                </div>
              </div>
            )}
          </>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="border-t border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-3">
        {messages.length > 0 && (
          <div className="flex justify-end mb-2">
            <button
              onClick={clearChat}
              className="text-xs text-gray-400 hover:text-red-500 flex items-center gap-1 transition-colors"
            >
              <Trash2 size={12} /> Clear chat
            </button>
          </div>
        )}
        <div className="flex items-end gap-2 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-600 rounded-xl px-3 py-2">
          <VoiceInput onTranscript={(text) => setInput((p) => p + text)} />
          <textarea
            ref={textareaRef}
            value={input}
            onInput={handleInput}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t('placeholder')}
            rows={1}
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-gray-400
                       dark:text-gray-200 resize-none py-1.5 leading-snug max-h-36"
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="bg-primary text-white p-2.5 rounded-lg hover:bg-primary-dark
                       disabled:opacity-40 transition-colors flex-shrink-0"
          >
            <Send size={15} />
          </button>
        </div>
        <p className="text-center text-xs text-gray-400 mt-2">
          NALSA Helpline: <a href="tel:18001110031" className="underline">1800-11-0031</a> (Free)
        </p>
      </div>
    </div>
  )
}
