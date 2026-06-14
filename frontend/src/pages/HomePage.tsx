import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search } from 'lucide-react';
import Navbar from '../components/shared/Navbar';

const EXAMPLE_QUERIES = [
  'Right to privacy Supreme Court',
  'Bail conditions NDPS Act',
  'Landmark RTI judgements',
  'Dowry harassment IPC 498A',
];

export default function HomePage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');

  const goToSearch = (searchQuery: string) => {
    const trimmed = searchQuery.trim();
    if (!trimmed) return;
    navigate(`/search?q=${encodeURIComponent(trimmed)}`);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    goToSearch(query);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-1 flex flex-col items-center justify-center px-6 pb-16">
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-primary mb-3">LexSearch</h1>
          <p className="text-lg text-subtext">Search Indian Legal Judgements with AI</p>
        </div>

        <form onSubmit={handleSearch} className="w-full max-w-2xl relative mb-6">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a legal question..."
            className="w-full px-5 py-4 pr-14 text-base border border-gray-200 rounded-full shadow-sm focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent"
          />
          <button
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2.5 bg-accent text-white rounded-full hover:bg-accent/90 transition-colors"
            aria-label="Search"
          >
            <Search className="w-5 h-5" />
          </button>
        </form>

        <div className="flex flex-wrap justify-center gap-2 max-w-2xl mb-12">
          {EXAMPLE_QUERIES.map((example) => (
            <button
              key={example}
              onClick={() => goToSearch(example)}
              className="px-3 py-1.5 text-sm text-subtext bg-white border border-gray-200 rounded-full hover:border-accent hover:text-accent transition-colors"
            >
              {example}
            </button>
          ))}
        </div>

        <p className="text-sm text-subtext">
          50,000+ Judgements · Supreme Court · 24 High Courts
        </p>
      </main>

      <footer className="py-6 text-center text-sm text-subtext border-t border-gray-100">
        About · GitHub · Feedback
      </footer>
    </div>
  );
}
