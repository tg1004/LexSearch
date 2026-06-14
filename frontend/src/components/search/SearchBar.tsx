import { Search } from 'lucide-react';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  placeholder?: string;
  compact?: boolean;
}

export default function SearchBar({
  value,
  onChange,
  onSubmit,
  placeholder = 'Ask a legal question...',
  compact = false,
}: SearchBarProps) {
  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="w-full relative">
      <input
        type="text"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        className={`w-full border border-gray-200 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent ${
          compact ? 'px-4 py-2.5 pr-12 text-sm' : 'px-5 py-4 pr-14 text-base'
        }`}
      />
      <button
        type="submit"
        className={`absolute right-2 top-1/2 -translate-y-1/2 bg-accent text-white rounded-full hover:bg-accent/90 transition-colors ${
          compact ? 'p-2' : 'p-2.5'
        }`}
        aria-label="Search"
      >
        <Search className={compact ? 'w-4 h-4' : 'w-5 h-5'} />
      </button>
    </form>
  );
}
