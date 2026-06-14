import { Link } from 'react-router-dom';
import type { Source } from '../../types/search.types';
import { formatDate } from '../../utils/formatDate';
import { highlightText } from '../../utils/highlightText';

interface SourceCardProps {
  source: Source;
  index: number;
  query: string;
  maxScore: number;
  id?: string;
}

export default function SourceCard({
  source,
  index,
  query,
  maxScore,
  id,
}: SourceCardProps) {
  const relevance = maxScore > 0 ? Math.min(100, Math.round((source.score / maxScore) * 100)) : 0;
  const snippet = source.snippet.length > 150 ? `${source.snippet.slice(0, 150)}...` : source.snippet;

  return (
    <article
      id={id}
      className="bg-white border border-gray-200 rounded-xl p-5 hover:border-gray-300 transition-colors scroll-mt-28"
    >
      <div className="flex items-start justify-between gap-3 mb-2">
        <div className="min-w-0">
          <span className="text-xs font-semibold text-accent mr-2">[{index}]</span>
          <Link
            to={`/document/${source.document_id}${
              source.chunk_index !== null && source.chunk_index !== undefined
                ? `?highlight=${source.chunk_index}`
                : ''
            }`}
            className="text-base font-semibold text-primary hover:text-accent transition-colors"
          >
            {source.title}
          </Link>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-subtext mb-3">
        {source.court && <span>{source.court}</span>}
        {source.court && source.date && <span>·</span>}
        {source.date && <span>{formatDate(source.date)}</span>}
      </div>

      <p
        className="text-sm text-[#444444] leading-6 mb-4"
        dangerouslySetInnerHTML={{ __html: highlightText(snippet, query) }}
      />

      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 max-w-xs">
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-accent/80 rounded-full transition-all"
              style={{ width: `${relevance}%` }}
            />
          </div>
        </div>
        <Link
          to={`/document/${source.document_id}${
            source.chunk_index !== null && source.chunk_index !== undefined
              ? `?highlight=${source.chunk_index}`
              : ''
          }`}
          className="text-sm font-medium text-accent hover:underline whitespace-nowrap"
        >
          Read Full Judgement
        </Link>
      </div>
    </article>
  );
}
