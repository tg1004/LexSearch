import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { ThumbsDown, ThumbsUp } from 'lucide-react';
import { submitFeedback } from '../../api/feedbackApi';

interface FeedbackButtonsProps {
  searchId: string;
  query: string;
  providerUsed?: string | null;
}

export default function FeedbackButtons({
  searchId,
  query,
  providerUsed,
}: FeedbackButtonsProps) {
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);

  const mutation = useMutation({
    mutationFn: (isHelpful: boolean) =>
      submitFeedback({
        query,
        is_helpful: isHelpful,
        provider_used: providerUsed,
        search_id: searchId,
      }),
    onSuccess: (_, isHelpful) => {
      setFeedback(isHelpful ? 'up' : 'down');
    },
  });

  const handleFeedback = (isHelpful: boolean) => {
    if (feedback || mutation.isPending) return;
    mutation.mutate(isHelpful);
  };

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={() => handleFeedback(true)}
        disabled={!!feedback || mutation.isPending}
        className={`p-1.5 rounded-lg transition-colors disabled:cursor-default ${
          feedback === 'up' ? 'text-green-600 bg-green-50' : 'text-subtext hover:bg-gray-100'
        }`}
        aria-label="Helpful"
        title="Helpful"
      >
        <ThumbsUp className="w-4 h-4" />
      </button>
      <button
        type="button"
        onClick={() => handleFeedback(false)}
        disabled={!!feedback || mutation.isPending}
        className={`p-1.5 rounded-lg transition-colors disabled:cursor-default ${
          feedback === 'down' ? 'text-red-600 bg-red-50' : 'text-subtext hover:bg-gray-100'
        }`}
        aria-label="Not helpful"
        title="Not helpful"
      >
        <ThumbsDown className="w-4 h-4" />
      </button>
      {feedback && (
        <span className="text-xs text-subtext">Thanks for your feedback</span>
      )}
      {mutation.isError && (
        <span className="text-xs text-red-600">Could not save feedback</span>
      )}
    </div>
  );
}
