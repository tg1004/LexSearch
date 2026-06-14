export default function SearchResultsSkeleton() {
  return (
    <div className="space-y-6 animate-pulse">
      <div className="flex items-center gap-2 text-sm text-subtext">
        <span>Searching 50,000+ judgements</span>
        <span className="inline-flex gap-1">
          <span className="w-1 h-1 bg-subtext rounded-full animate-bounce" />
          <span className="w-1 h-1 bg-subtext rounded-full animate-bounce [animation-delay:150ms]" />
          <span className="w-1 h-1 bg-subtext rounded-full animate-bounce [animation-delay:300ms]" />
        </span>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-6 space-y-4">
        <div className="h-5 w-32 bg-gray-100 rounded" />
        <div className="space-y-2">
          <div className="h-4 w-full bg-gray-100 rounded" />
          <div className="h-4 w-11/12 bg-gray-100 rounded" />
          <div className="h-4 w-4/5 bg-gray-100 rounded" />
        </div>
        <div className="h-8 w-40 bg-gray-100 rounded-full" />
      </div>

      <div className="space-y-4">
        <div className="h-6 w-28 bg-gray-100 rounded" />
        {Array.from({ length: 5 }).map((_, index) => (
          <div key={index} className="bg-white border border-gray-200 rounded-xl p-5 space-y-3">
            <div className="h-5 w-3/4 bg-gray-100 rounded" />
            <div className="h-4 w-1/3 bg-gray-100 rounded" />
            <div className="h-4 w-full bg-gray-100 rounded" />
            <div className="h-4 w-5/6 bg-gray-100 rounded" />
          </div>
        ))}
      </div>
    </div>
  );
}
