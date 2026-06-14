import { Zap } from 'lucide-react';

interface ProviderBadgeProps {
  provider: string;
  model?: string | null;
}

const PROVIDER_LABELS: Record<string, string> = {
  groq: 'Groq',
  gemini: 'Gemini',
  ollama: 'Ollama',
  auto: 'Auto',
};

function formatModelName(model: string): string {
  return model
    .replace('llama-', 'Llama ')
    .replace('-versatile', '')
    .replace('gemini-', 'Gemini ')
    .replace(/-/g, ' ');
}

export default function ProviderBadge({ provider, model }: ProviderBadgeProps) {
  const label = PROVIDER_LABELS[provider.toLowerCase()] ?? provider;
  const modelLabel = model ? formatModelName(model) : null;

  return (
    <div className="inline-flex items-center gap-1.5 text-xs text-subtext bg-gray-50 border border-gray-100 rounded-full px-2.5 py-1">
      <Zap className="w-3.5 h-3.5 text-amber-500" />
      <span>
        {label}
        {modelLabel ? ` · ${modelLabel}` : ''}
      </span>
    </div>
  );
}
