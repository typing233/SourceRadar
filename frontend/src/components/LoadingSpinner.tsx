export default function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClass = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-12 w-12' : 'h-8 w-8'
  return (
    <div className="flex justify-center items-center p-8">
      <div className={`animate-spin rounded-full ${sizeClass} border-b-2 border-blue-600`}></div>
    </div>
  )
}
