export function escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function highlightText(text: string, query: string): string {
  const safeText = escapeHtml(text);
  const terms = query
    .split(/\s+/)
    .map((term) => term.trim())
    .filter((term) => term.length > 2);

  if (!terms.length) {
    return safeText;
  }

  const pattern = new RegExp(`(${terms.map(escapeRegExp).join('|')})`, 'gi');
  return safeText.replace(pattern, '<mark class="bg-yellow-200 rounded px-0.5">$1</mark>');
}
