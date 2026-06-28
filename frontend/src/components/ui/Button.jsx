import clsx from 'clsx'

export function Button({ children, variant = 'primary', size = 'md', className, disabled, ...props }) {
  return (
    <button
      className={clsx(
        'inline-flex items-center justify-center font-medium rounded-lg transition-all focus:outline-none focus:ring-2 focus:ring-offset-2',
        variant === 'primary' && 'bg-primary text-white hover:bg-primary-dark focus:ring-primary disabled:opacity-50',
        variant === 'secondary' && 'bg-white text-primary border border-primary hover:bg-blue-50 focus:ring-primary',
        variant === 'ghost' && 'text-gray-600 hover:bg-gray-100 focus:ring-gray-300',
        size === 'sm' && 'px-3 py-1.5 text-sm',
        size === 'md' && 'px-4 py-2 text-sm',
        size === 'lg' && 'px-6 py-3 text-base',
        disabled && 'cursor-not-allowed',
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
