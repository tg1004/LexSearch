import type { DocumentDetail } from '../../types/document.types';
import HighlightedText from './HighlightedText';

interface DocumentViewerProps {
  document: DocumentDetail;
  highlightPassage?: string | null;
}

export default function DocumentViewer({
  document,
  highlightPassage,
}: DocumentViewerProps) {
  return (
    <section className="bg-white border border-gray-200 rounded-2xl p-6 md:p-8 shadow-sm">
      <h2 className="text-lg font-semibold text-primary mb-6 pb-3 border-b border-gray-100">
        Full Judgement
      </h2>
      <HighlightedText
        fullText={document.full_text}
        highlightPassage={highlightPassage}
      />
    </section>
  );
}
