interface RelatedQuestionsProps {
  questions: string[];
  onSelect: (question: string) => void;
}

export default function RelatedQuestions({ questions, onSelect }: RelatedQuestionsProps) {
  if (!questions.length) {
    return null;
  }

  return (
    <section className="mt-8">
      <h2 className="text-lg font-semibold text-primary mb-3">People also ask</h2>
      <div className="flex flex-wrap gap-2">
        {questions.map((question) => (
          <button
            key={question}
            type="button"
            onClick={() => onSelect(question)}
            className="px-3 py-2 text-sm text-primary bg-white border border-gray-200 rounded-full hover:border-accent hover:text-accent transition-colors text-left"
          >
            {question}
          </button>
        ))}
      </div>
    </section>
  );
}
