import type { ProviderInfo, PreferredProvider } from '../../types/search.types';

interface ModelSelectorProps {
  providers: ProviderInfo[];
  selected: PreferredProvider;
  onChange: (provider: PreferredProvider) => void;
  isLoading?: boolean;
}

export default function ModelSelector({
  providers,
  selected,
  onChange,
  isLoading = false,
}: ModelSelectorProps) {
  if (isLoading) {
    return (
      <div className="flex gap-2">
        {[1, 2, 3].map((item) => (
          <div key={item} className="h-8 w-24 bg-gray-100 rounded-full animate-pulse" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <span className="text-sm text-subtext mr-1">Model:</span>
      {providers.map((provider) => {
        const isSelected = selected === provider.name;
        const isDisabled = !provider.available;

        return (
          <button
            key={provider.name}
            type="button"
            disabled={isDisabled}
            onClick={() => onChange(provider.name as PreferredProvider)}
            className={`px-3 py-1.5 text-sm rounded-full border transition-colors ${
              isSelected
                ? 'bg-primary text-white border-primary'
                : 'bg-white text-primary border-gray-200 hover:border-accent'
            } ${isDisabled ? 'opacity-40 cursor-not-allowed' : ''}`}
            title={provider.model ? `${provider.label} · ${provider.model}` : provider.label}
          >
            {provider.label.replace(' (Recommended)', '').replace(' (Fastest)', '').replace(' (Balanced)', '')}
          </button>
        );
      })}
    </div>
  );
}
