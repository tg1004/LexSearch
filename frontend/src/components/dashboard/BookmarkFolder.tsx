interface BookmarkFolderProps {
  name: string;
  count: number;
  isActive: boolean;
  onSelect: () => void;
}

export default function BookmarkFolder({ name, count, isActive, onSelect }: BookmarkFolderProps) {
  return (
    <button
      type="button"
      onClick={onSelect}
      className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
        isActive
          ? 'bg-accent/10 text-accent font-medium'
          : 'text-subtext hover:bg-gray-100 hover:text-primary'
      }`}
    >
      <span className="truncate block">{name}</span>
      <span className="text-xs opacity-70">{count}</span>
    </button>
  );
}
