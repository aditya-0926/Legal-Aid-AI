import { useState } from 'react'
import { BookOpen, ChevronDown, ChevronUp, FileText, Database } from 'lucide-react'

export function SourcesCitation({ citations }) {
  const [open, setOpen] = useState(false)
  // support both `citations` and legacy `sources` prop name
  const items = citations ?? []
  if (!items.length) return null

  return (
    <div className="border border-gray-100 dark:border-gray-700 rounded-xl overflow-hidden text-sm">
      <button
        onClick={() => setOpen((p) => !p)}
        className="w-full flex items-center justify-between px-4 py-2.5 font-medium
                   text-gray-600 dark:text-gray-400 hover:bg-gray-50
                   dark:hover:bg-gray-700/50 transition-colors"
      >
        <span className="flex items-center gap-1.5">
          <BookOpen size={13} />
          Legal Citations ({items.length})
        </span>
        {open ? <ChevronUp size={13} /> : <ChevronDown size={13} />}
      </button>

      {open && (
        <div className="divide-y divide-gray-100 dark:divide-gray-700 bg-gray-50 dark:bg-gray-800/40">
          {items.map((c, i) => (
            <div key={i} className="px-4 py-3 space-y-1">
              {/* Act name + source badge */}
              <div className="flex items-start justify-between gap-2">
                <p className="font-semibold text-gray-800 dark:text-gray-200 leading-snug">
                  {c.act_name}
                </p>
                <span className={`flex-shrink-0 text-[10px] px-1.5 py-0.5 rounded font-medium ${
                  c.source === 'built-in'
                    ? 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-400'
                    : 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-400'
                }`}>
                  {c.source === 'built-in' ? '📦 Built-in' : '📤 Uploaded'}
                </span>
              </div>

              {/* Section */}
              <p className="text-primary dark:text-blue-400 font-medium text-xs">
                {c.section}
              </p>

              {/* Chapter */}
              {c.chapter && (
                <p className="text-gray-500 dark:text-gray-400 text-xs">{c.chapter}</p>
              )}

              {/* Page number */}
              {c.page_number > 0 && (
                <p className="text-gray-400 text-xs flex items-center gap-1">
                  <FileText size={10} /> Page {c.page_number}
                </p>
              )}

              {/* Excerpt */}
              <p className="text-gray-500 dark:text-gray-400 text-xs leading-relaxed line-clamp-3 mt-1">
                "{c.excerpt}"
              </p>

              {/* Relevance */}
              <div className="flex items-center gap-2 pt-0.5">
                <div className="flex-1 h-1 bg-gray-200 dark:bg-gray-600 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full"
                    style={{ width: `${Math.round(c.relevance_score * 100)}%` }}
                  />
                </div>
                <span className="text-[10px] text-gray-400">
                  {Math.round(c.relevance_score * 100)}% relevant
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
