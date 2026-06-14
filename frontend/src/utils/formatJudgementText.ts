export type JudgementBlockType = 'header' | 'subheader' | 'caption' | 'paragraph';

export interface JudgementBlock {
  type: JudgementBlockType;
  text: string;
}

const SKIP_LINE_PATTERNS: RegExp[] = [
  /^\[Cites/i,
  /^,?\s*Cited by/i,
  /^Equivalent citations:/i,
  /^Author:/i,
  /^Bench:/i,
  /^REPORTABLE$/i,
  /^Share Link/i,
  /^Downloaded on/i,
  /^Indian Kanoon/i,
  /^Free features/i,
  /^Premium Member/i,
  /^Cites\s+\d+/i,
];

const HEADER_LINE_PATTERNS: RegExp[] = [
  /^IN THE SUPREME COURT/i,
  /^IN THE HIGH COURT/i,
  /^SUPREME COURT OF INDIA/i,
  /^JUDGMENT$/i,
  /^J U D G M E N T$/i,
  /^ORDER$/i,
  /^O R D E R$/i,
  /^(CRIMINAL|CIVIL)\s+(APPEAL|PETITION|SUIT)/i,
  /JURISDICTION$/i,
];

function shouldSkipLine(line: string): boolean {
  if (!line.trim()) return true;
  if (/^\d+$/.test(line.trim())) return true;
  return SKIP_LINE_PATTERNS.some((pattern) => pattern.test(line));
}

function isHeaderLine(line: string): boolean {
  if (HEADER_LINE_PATTERNS.some((pattern) => pattern.test(line))) return true;
  const trimmed = line.trim();
  return (
    trimmed.length >= 10 &&
    trimmed.length <= 90 &&
    trimmed === trimmed.toUpperCase() &&
    /[A-Z]/.test(trimmed) &&
    !/^\d/.test(trimmed)
  );
}

function isSubheaderLine(line: string): boolean {
  return /,\s*J\.?\s*$/i.test(line) || /^Hon'ble/i.test(line) || /^Before:/i.test(line);
}

function isCaptionLine(line: string): boolean {
  return /^(Versus|Vs\.|V\.\s*S\.|Appellant|Respondent|Petitioner|Plaintiff|Defendant)/i.test(
    line,
  );
}

function isNumberedParagraph(line: string): boolean {
  return /^\d+\.\s/.test(line);
}

function normalizeWhitespace(text: string): string {
  return text.replace(/\s+/g, ' ').trim();
}

function flushBuffer(buffer: string[]): JudgementBlock | null {
  if (!buffer.length) return null;
  const text = normalizeWhitespace(buffer.join(' '));
  return text ? { type: 'paragraph', text } : null;
}

/**
 * Converts raw Indian Kanoon judgement text into readable blocks for display.
 */
export function formatJudgementText(raw: string): JudgementBlock[] {
  const lines = raw
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n')
    .map((line) => line.trim());

  const blocks: JudgementBlock[] = [];
  let buffer: string[] = [];
  let passedMetadata = false;

  const pushBlock = (block: JudgementBlock | null) => {
    if (block) blocks.push(block);
  };

  for (const line of lines) {
    if (!line || shouldSkipLine(line)) continue;

    // Skip duplicate title/court lines before the formal caption starts.
    if (!passedMetadata) {
      if (
        isHeaderLine(line) ||
        isCaptionLine(line) ||
        isSubheaderLine(line) ||
        isNumberedParagraph(line) ||
        /^JUDGMENT|^ORDER/i.test(line)
      ) {
        passedMetadata = true;
      } else if (
        line.includes(' on ') &&
        (line.includes(' vs ') || line.includes(' Vs '))
      ) {
        continue;
      } else if (line.split(' ').length > 12 && line.includes('SUPREME COURT')) {
        continue;
      }
    }

    if (isHeaderLine(line)) {
      pushBlock(flushBuffer(buffer));
      buffer = [];
      blocks.push({ type: 'header', text: line });
      continue;
    }

    if (isSubheaderLine(line)) {
      pushBlock(flushBuffer(buffer));
      buffer = [];
      blocks.push({ type: 'subheader', text: line });
      continue;
    }

    if (isCaptionLine(line)) {
      pushBlock(flushBuffer(buffer));
      buffer = [];
      blocks.push({ type: 'caption', text: line });
      continue;
    }

    if (isNumberedParagraph(line)) {
      pushBlock(flushBuffer(buffer));
      buffer = [line];
      continue;
    }

    // Short standalone lines ending with a period are often their own paragraph.
    if (buffer.length && line.endsWith('.') && line.length < 120 && buffer.join(' ').endsWith('.')) {
      buffer.push(line);
      pushBlock(flushBuffer(buffer));
      buffer = [];
      continue;
    }

    buffer.push(line);
  }

  pushBlock(flushBuffer(buffer));

  if (!blocks.length && raw.trim()) {
    return [{ type: 'paragraph', text: normalizeWhitespace(raw) }];
  }

  return blocks;
}

/**
 * Split block text around a highlight passage for rendering.
 */
export function splitAroundHighlight(
  text: string,
  highlightPassage: string | null,
): { before: string; highlight: string; after: string } {
  if (!highlightPassage?.trim()) {
    return { before: text, highlight: '', after: '' };
  }

  const normalizedText = normalizeWhitespace(text);
  const normalizedPassage = normalizeWhitespace(highlightPassage);

  const directIndex = normalizedText.indexOf(normalizedPassage);
  if (directIndex >= 0) {
    return {
      before: normalizedText.slice(0, directIndex),
      highlight: normalizedPassage,
      after: normalizedText.slice(directIndex + normalizedPassage.length),
    };
  }

  // Fuzzy: find first 60 chars of passage
  const snippet = normalizedPassage.slice(0, Math.min(80, normalizedPassage.length));
  const fuzzyIndex = normalizedText.indexOf(snippet);
  if (fuzzyIndex >= 0) {
    const end = Math.min(fuzzyIndex + normalizedPassage.length, normalizedText.length);
    return {
      before: normalizedText.slice(0, fuzzyIndex),
      highlight: normalizedText.slice(fuzzyIndex, end),
      after: normalizedText.slice(end),
    };
  }

  return { before: text, highlight: '', after: '' };
}
