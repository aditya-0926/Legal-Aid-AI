export function TypingIndicator() {
  return (
    <div className="flex items-center gap-1.5 px-4 py-3.5">
      <span className="text-xs text-gray-400 mr-1">Analyzing...</span>
      {[0, 160, 320].map((delay) => (
        <span
          key={delay}
          className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"
          style={{ animationDelay: `${delay}ms` }}
        />
      ))}
    </div>
  )
}
