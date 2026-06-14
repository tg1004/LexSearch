import { useEffect, useMemo } from 'react';
import {
  formatJudgementText,
  splitAroundHighlight,
  type JudgementBlock,
} from '../../utils/formatJudgementText';

interface HighlightedTextProps {
  fullText: string;
  highlightPassage?: string | null;
}

function blockClassName(type: JudgementBlock['type']): string {
  switch (type) {
    case 'header':
      return 'text-sm font-semibold tracking-wide text-primary uppercase mt-8 mb-3 first:mt-0';
    case 'subheader':
      return 'text-base font-semibold text-primary mt-6 mb-2 italic';
    case 'caption':
      return 'text-[15px] font-medium text-[#444444] leading-7';
    case 'paragraph':
    default:
      return 'text-[16px] leading-[1.75] text-[#333333] mb-4 text-justify';
  }
}

function renderBlockText(text: string, highlightPassage: string | null | undefined) {
  const parts = splitAroundHighlight(text, highlightPassage ?? null);

  if (!parts.highlight) {
    return <>{parts.before}{parts.after}</>;
  }

  return (
    <>
      {parts.before}
      <mark
        id="highlight-passage"
        className="bg-yellow-200 rounded px-0.5 scroll-mt-32 not-italic font-normal"
      >
        {parts.highlight}
      </mark>
      {parts.after}
    </>
  );
}

export default function HighlightedText({
  fullText,
  highlightPassage,
}: HighlightedTextProps) {
  const blocks = useMemo(() => formatJudgementText(fullText), [fullText]);

  const highlightBlockIndex = useMemo(() => {
    if (!highlightPassage?.trim()) return -1;
    const passage = highlightPassage.replace(/\s+/g, ' ').trim();
    return blocks.findIndex((block) => {
      const normalized = block.text.replace(/\s+/g, ' ');
      return normalized.includes(passage) || passage.includes(normalized.slice(0, 60));
    });
  }, [blocks, highlightPassage]);

  useEffect(() => {
    const element = document.getElementById('highlight-passage');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [highlightPassage, highlightBlockIndex]);

  return (
    <article className="judgement-content max-w-none">
      {blocks.map((block, index) => {
        const Tag = block.type === 'header' ? 'h3' : block.type === 'subheader' ? 'h4' : 'p';
        const isHighlightBlock = index === highlightBlockIndex;

        if (block.type === 'caption') {
          return (
            <p key={`${block.type}-${index}`} className={blockClassName(block.type)}>
              {renderBlockText(
                block.text,
                isHighlightBlock ? highlightPassage : null,
              )}
            </p>
          );
        }

        return (
          <Tag key={`${block.type}-${index}`} className={blockClassName(block.type)}>
            {renderBlockText(
              block.text,
              isHighlightBlock ? highlightPassage : null,
            )}
          </Tag>
        );
      })}
    </article>
  );
}
