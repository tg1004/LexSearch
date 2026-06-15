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

const STOPWORDS = new Set([
  'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'as', 'by',
  'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
  'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'shall', 'can',
  'this', 'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'we', 'our',
  'you', 'your', 'he', 'she', 'his', 'her', 'with', 'from', 'into', 'about', 'over',
  'after', 'before', 'between', 'under', 'again', 'further', 'then', 'once', 'here',
  'there', 'when', 'where', 'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other',
  'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
  'just', 'also', 'any', 'what', 'which', 'who', 'whom', 'while', 'during', 'through',
]);

/** Short legal tokens worth highlighting even when under 4 chars. */
const LEGAL_SHORT_TERMS = new Set([
  'ipc', 'rti', 'act', 'sec', 'art', 'hc', 'sc', 'ndps', 'crpc', 'bail', 'uoi', 'vs',
]);

/**
 * Extract meaningful legal/search terms — skip common English stopwords.
 */
export function extractHighlightTerms(query: string): string[] {
  const terms: string[] = [];

  const quoted = query.match(/"([^"]+)"/g);
  if (quoted) {
    for (const segment of quoted) {
      const phrase = segment.replace(/"/g, '').trim();
      if (phrase.length >= 3) {
        terms.push(phrase);
      }
    }
  }

  const words = query
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .map((word) => word.trim())
    .filter(Boolean);

  for (const word of words) {
    if (LEGAL_SHORT_TERMS.has(word)) {
      terms.push(word);
      continue;
    }
    if (word.length < 4) continue;
    if (STOPWORDS.has(word)) continue;
    terms.push(word);
  }

  return [...new Set(terms.map((term) => term.trim()).filter(Boolean))];
}

export function highlightText(text: string, query: string): string {
  const safeText = escapeHtml(text);
  const terms = extractHighlightTerms(query);

  if (!terms.length) {
    return safeText;
  }

  const pattern = new RegExp(
    `(${terms.map((term) => (term.includes(' ') ? escapeRegExp(term) : `\\b${escapeRegExp(term)}\\b`)).join('|')})`,
    'gi',
  );
  return safeText.replace(
    pattern,
    '<mark class="bg-yellow-200 rounded px-0.5">$1</mark>',
  );
}
