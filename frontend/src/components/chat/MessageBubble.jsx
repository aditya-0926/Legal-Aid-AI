import ReactMarkdown from 'react-markdown'
import { DomainBadge } from '../legal/DomainBadge'
import { RightsCard } from '../legal/RightsCard'
import { NextStepsPanel } from '../legal/NextStepsPanel'
import { LegalCenterMap } from '../legal/LegalCenterMap'
import { SourcesCitation } from '../legal/SourcesCitation'
import { ConfidenceBar } from '../legal/ConfidenceBar'

export function MessageBubble({ message }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex justify-end">
        <div className="max-w-[82%] bg-primary text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm leading-relaxed">
          {message.content}
        </div>
      </div>
    )
  }

  const res = message.content
  const isError = res.isError
  const citations = res.citations ?? res.sources ?? []

  return (
    <div className="flex justify-start">
      <div className="max-w-[92%] w-full space-y-3">

        {/* Domain badge + confidence */}
        {res.domain && res.domain !== 'general' && !isError && (
          <div className="flex items-center gap-3 flex-wrap">
            <DomainBadge domain={res.domain} confidence={res.domain_confidence} />
            {res.confidence > 0 && <ConfidenceBar score={res.confidence} />}
          </div>
        )}

        {/* Main answer bubble */}
        <div className={`bg-white dark:bg-gray-800 border rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm
          ${isError
            ? 'border-red-200 dark:border-red-700 bg-red-50 dark:bg-red-900/20'
            : 'border-gray-100 dark:border-gray-700'
          }`}
        >
          <div className="text-sm text-gray-800 dark:text-gray-200 prose prose-sm dark:prose-invert max-w-none">
            <ReactMarkdown>{res.answer}</ReactMarkdown>
          </div>
        </div>

        {/* Structured panels */}
        {!isError && (
          <>
            {res.rights_summary?.length > 0 && (
              <RightsCard rights={res.rights_summary} />
            )}
            {res.next_steps?.length > 0 && (
              <NextStepsPanel steps={res.next_steps} />
            )}

            {/* Citations — always shown when available */}
            {citations.length > 0 && (
              <SourcesCitation citations={citations} />
            )}

            {res.nearby_centers?.length > 0 && (
              <LegalCenterMap centers={res.nearby_centers} />
            )}
          </>
        )}
      </div>
    </div>
  )
}
