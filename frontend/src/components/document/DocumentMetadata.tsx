import { formatDate } from '../../utils/formatDate';
import type { DocumentDetail } from '../../types/document.types';

interface DocumentMetadataProps {
  document: DocumentDetail;
}

export default function DocumentMetadata({ document }: DocumentMetadataProps) {
  const metadataItems = [
    document.court,
    document.date ? formatDate(document.date) : null,
    document.bench_size,
    document.case_type,
    document.outcome,
  ].filter(Boolean);

  return (
    <div className="space-y-3">
      {metadataItems.length > 0 && (
        <div className="flex flex-wrap items-center gap-x-2 gap-y-1 text-sm text-subtext">
          {metadataItems.map((item, index) => (
            <span key={`${item}-${index}`} className="inline-flex items-center gap-2">
              {index > 0 && <span>·</span>}
              <span>{item}</span>
            </span>
          ))}
        </div>
      )}

      {document.judges.length > 0 && (
        <p className="text-sm text-subtext">
          <span className="font-medium text-primary">Before: </span>
          {document.judges.join(', ')}
        </p>
      )}
    </div>
  );
}
