import { Clock, Search, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useSearchHistory } from '../../hooks/useHistory';
import { formatDate } from '../../utils/formatDate';
import ErrorMessage from '../shared/ErrorMessage';
import LoadingSpinner from '../shared/LoadingSpinner';

export default function SearchHistory() {
  const navigate = useNavigate();
  const { items, isLoading, error, clearAll, removeEntry, isClearing } = useSearchHistory();

  if (isLoading) {
    return (
      <div className="flex justify-center py-12">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <ErrorMessage
        message={error instanceof Error ? error.message : 'Failed to load search history'}
      />
    );
  }

  if (!items.length) {
    return (
      <div className="text-center py-16">
        <Search className="w-10 h-10 text-gray-300 mx-auto mb-3" />
        <p className="text-primary font-medium mb-1">No search history yet</p>
        <p className="text-sm text-subtext">Your recent searches will appear here.</p>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-primary">Search History</h2>
        <button
          type="button"
          onClick={() => clearAll()}
          disabled={isClearing}
          className="text-sm text-red-600 hover:underline disabled:opacity-50"
        >
          Clear all history
        </button>
      </div>

      <ul className="space-y-3">
        {items.map((item) => (
          <li
            key={item.id}
            className="flex items-start gap-4 p-4 bg-white border border-gray-200 rounded-xl hover:border-accent/30 transition-colors"
          >
            <button
              type="button"
              onClick={() => navigate(`/search?q=${encodeURIComponent(item.query)}`)}
              className="flex-1 text-left min-w-0"
            >
              <p className="font-medium text-primary truncate">{item.query}</p>
              <div className="flex flex-wrap items-center gap-2 mt-1 text-xs text-subtext">
                <span className="inline-flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {formatDate(item.searched_at)}
                </span>
                {item.provider_used && <span>· {item.provider_used}</span>}
                {item.result_count !== null && (
                  <span>· {item.result_count} result{item.result_count === 1 ? '' : 's'}</span>
                )}
              </div>
            </button>
            <button
              type="button"
              onClick={() => removeEntry(item.id)}
              className="p-2 text-subtext hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors shrink-0"
              aria-label="Delete search"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
