export default function LoadingSpinner({ size = 'md' }: { size?: 'sm' | 'md' | 'lg' }) {
  const sizeClass = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-8 h-8' : 'w-6 h-6';

  return (
    <div
      className={`${sizeClass} border-2 border-gray-200 border-t-accent rounded-full animate-spin`}
      role="status"
      aria-label="Loading"
    />
  );
}
