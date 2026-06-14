interface CitationBadgeProps {
  number: number;
  onClick?: (number: number) => void;
}

export default function CitationBadge({ number, onClick }: CitationBadgeProps) {
  return (
    <button
      type="button"
      onClick={() => onClick?.(number)}
      className="inline-flex items-center justify-center min-w-[1.35rem] h-5 px-1 mx-0.5 text-xs font-semibold text-accent bg-accent/10 rounded hover:bg-accent/20 transition-colors align-super"
      title={`View source [${number}]`}
    >
      [{number}]
    </button>
  );
}
