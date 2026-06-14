import { Sparkles } from 'lucide-react';
import type { Citation } from '../../types/search.types';
import CitationBadge from './CitationBadge';
import FeedbackButtons from './FeedbackButtons';
import ProviderBadge from './ProviderBadge';

interface AIAnswerProps {
  answer: string;
  citations: Citation[];
  providerUsed: string | null;
  providerModel?: string | null;
  searchId: string;
  query: string;
  preferredProvider: string;
  onCitationClick?: (number: number) => void;
  isUnavailable?: boolean;
  showFallbackWarning?: boolean;
  fallbackFrom?: string;
}

function renderAnswerWithCitations(
  answer: string,
  onCitationClick?: (number: number) => void,
) {
  const parts = answer.split(/(\[\d+\])/g);

  return parts.map((part, index) => {
    const match = part.match(/^\[(\d+)\]$/);
    if (match) {
      const number = Number(match[1]);
      return (
        <CitationBadge
          key={`${part}-${index}`}
          number={number}
          onClick={onCitationClick}
        />
      );
    }
    return <span key={`${part}-${index}`}>{part}</span>;
  });
}

export default function AIAnswer({
  answer,
  citations,
  providerUsed,
  providerModel,
  searchId,
  query,
  preferredProvider,
  onCitationClick,
  isUnavailable = false,
  showFallbackWarning = false,
  fallbackFrom,
}: AIAnswerProps) {
  return (
    <section className="bg-white border border-gray-200 rounded-2xl shadow-sm p-6">
      <div className="flex items-center gap-2 mb-4">
        <Sparkles className="w-5 h-5 text-accent" />
        <h2 className="text-lg font-semibold text-primary">AI Answer</h2>
      </div>

      {showFallbackWarning && fallbackFrom && providerUsed && (
        <div className="mb-4 text-sm text-amber-800 bg-amber-50 border border-amber-100 rounded-lg px-3 py-2">
          {fallbackFrom} unavailable — answered by {providerUsed}
        </div>
      )}

      <div
        className={`text-[15px] leading-7 ${
          isUnavailable ? 'text-subtext italic' : 'text-[#333333]'
        }`}
      >
        {renderAnswerWithCitations(answer, onCitationClick)}
      </div>

      {citations.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <p className="text-xs font-medium text-subtext mb-2">Cited sources</p>
          <div className="space-y-2">
            {citations.map((citation) => (
              <button
                key={citation.number}
                type="button"
                onClick={() => onCitationClick?.(citation.number)}
                className="block w-full text-left text-sm text-subtext hover:text-accent transition-colors"
              >
                <span className="font-medium text-accent mr-2">[{citation.number}]</span>
                {citation.title}
                {citation.court ? ` · ${citation.court}` : ''}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="mt-5 flex items-center justify-between gap-4 flex-wrap">
        <FeedbackButtons
          searchId={searchId}
          query={query}
          providerUsed={providerUsed}
        />
        {providerUsed && preferredProvider !== 'unavailable' && (
          <ProviderBadge provider={providerUsed} model={providerModel} />
        )}
      </div>
    </section>
  );
}
