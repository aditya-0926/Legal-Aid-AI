import clsx from 'clsx'

export function Input({ className, ...props }) {
  return (
    <input
      className={clsx(
        'w-full px-4 py-2.5 border border-gray-200 rounded-lg text-sm',
        'focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent',
        'placeholder:text-gray-400',
        className
      )}
      {...props}
    />
  )
}
