import { useEffect, useState } from 'react';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';
import {
  ArrowLeft,
  Bookmark,
  BookmarkCheck,
  Bot,
  Download,
  ExternalLink,
} from 'lucide-react';
import DocumentMetadata from '../components/document/DocumentMetadata';
import DocumentSummary from '../components/document/DocumentSummary';
import DocumentViewer from '../components/document/DocumentViewer';
import ErrorMessage from '../components/shared/ErrorMessage';
import LoadingSpinner from '../components/shared/LoadingSpinner';
import Navbar from '../components/shared/Navbar';
import { useAuth } from '../hooks/useAuth';
import { useBookmarks } from '../hooks/useBookmarks';
import {
  useDocument,
  useDocumentHighlight,
  useDocumentSummary,
} from '../hooks/useDocument';

function parseChunkIndex(value: string | null): number | null {
  if (!value) return null;
  const parsed = Number(value);
  return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
}

export default function DocumentPage() {
  const navigate = useNavigate();
  const { documentId = '' } = useParams();
  const [searchParams] = useSearchParams();
  const chunkIndex = parseChunkIndex(searchParams.get('highlight'));
  const { isAuthenticated } = useAuth();
  const { items, folders, addBookmark, isSaving } = useBookmarks(isAuthenticated);

  const [summaryEnabled, setSummaryEnabled] = useState(false);
  const [summaryText, setSummaryText] = useState<string | null>(null);
  const [showJumpButton, setShowJumpButton] = useState(false);
  const [showBookmarkModal, setShowBookmarkModal] = useState(false);
  const [bookmarkFolder, setBookmarkFolder] = useState('General');
  const [bookmarkNotes, setBookmarkNotes] = useState('');
  const [bookmarkSaved, setBookmarkSaved] = useState(false);
  const [bookmarkError, setBookmarkError] = useState<string | null>(null);

  const {
    data: document,
    isLoading,
    error,
  } = useDocument(documentId);

  const {
    data: highlight,
    isLoading: highlightLoading,
  } = useDocumentHighlight(documentId, chunkIndex);

  const {
    data: summaryResult,
    isLoading: summaryLoading,
    error: summaryError,
    refetch: refetchSummary,
  } = useDocumentSummary(documentId, summaryEnabled);

  useEffect(() => {
    if (document?.summary) {
      setSummaryText(document.summary);
      return;
    }
    if (document && !summaryEnabled) {
      setSummaryEnabled(true);
    }
  }, [document, summaryEnabled]);

  useEffect(() => {
    if (summaryResult?.summary) {
      setSummaryText(summaryResult.summary);
    }
  }, [summaryResult?.summary]);

  useEffect(() => {
    if (!highlight?.highlighted_passage) {
      setShowJumpButton(false);
      return;
    }

    const handleScroll = () => {
      const element = window.document.getElementById('highlight-passage');
      if (!element) {
        setShowJumpButton(false);
        return;
      }
      const rect = element.getBoundingClientRect();
      const isVisible = rect.top >= 80 && rect.bottom <= window.innerHeight - 80;
      setShowJumpButton(!isVisible);
    };

    handleScroll();
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [highlight?.highlighted_passage, highlightLoading]);

  const handleExportPdf = () => {
    window.print();
  };

  const existingBookmark = items.find((item) => item.document_id === documentId);

  const openBookmarkModal = () => {
    setBookmarkError(null);
    setShowBookmarkModal(true);
  };

  const handleBookmarkClick = () => {
    if (!isAuthenticated) {
      openBookmarkModal();
      return;
    }
    if (existingBookmark) {
      setBookmarkSaved(true);
      return;
    }
    openBookmarkModal();
  };

  const handleSaveBookmark = async () => {
    if (!documentId) return;
    setBookmarkError(null);
    try {
      await addBookmark({
        document_id: documentId,
        folder_name: bookmarkFolder,
        notes: bookmarkNotes || undefined,
      });
      setBookmarkSaved(true);
      setShowBookmarkModal(false);
    } catch (err) {
      setBookmarkError(
        err instanceof Error ? err.message : 'Failed to save bookmark. Please try again.',
      );
    }
  };

  const handleJumpToHighlight = () => {
    window.document.getElementById('highlight-passage')?.scrollIntoView({
      behavior: 'smooth',
      block: 'center',
    });
  };

  if (!documentId) {
    return (
      <div className="min-h-screen flex items-center justify-center px-6">
        <p className="text-subtext">Invalid document ID.</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 print:bg-white">
      <header className="bg-white border-b border-gray-100 print:hidden">
        <div className="max-w-3xl mx-auto flex items-center justify-between gap-4 px-4 sm:px-6 py-3">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-2 text-sm text-subtext hover:text-accent transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to results
          </button>
        </div>
        <Navbar compact />
      </header>

      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6 space-y-6">
        {isLoading && (
          <div className="flex justify-center py-20">
            <LoadingSpinner size="lg" />
          </div>
        )}

        {error && (
          <ErrorMessage
            message={error instanceof Error ? error.message : 'Failed to load document'}
          />
        )}

        {document && (
          <>
            <div className="flex flex-wrap items-start justify-between gap-4 print:hidden">
              <div className="flex-1 min-w-0" />
              <div className="flex flex-wrap items-center gap-2">
                <button
                  type="button"
                  onClick={() => setSummaryEnabled(true)}
                  className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-gray-200 rounded-lg hover:border-accent transition-colors"
                >
                  <Bot className="w-4 h-4" />
                  Summary
                </button>
                <button
                  type="button"
                  onClick={handleExportPdf}
                  className="inline-flex items-center gap-2 px-3 py-2 text-sm border border-gray-200 rounded-lg hover:border-accent transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Export PDF
                </button>
                <button
                  type="button"
                  onClick={handleBookmarkClick}
                  disabled={isSaving || !!existingBookmark || bookmarkSaved}
                  className={`inline-flex items-center gap-2 px-3 py-2 text-sm border rounded-lg transition-colors ${
                    existingBookmark || bookmarkSaved
                      ? 'border-green-200 text-green-700 bg-green-50'
                      : 'border-gray-200 hover:border-accent'
                  }`}
                >
                  {existingBookmark || bookmarkSaved ? (
                    <BookmarkCheck className="w-4 h-4" />
                  ) : (
                    <Bookmark className="w-4 h-4" />
                  )}
                  {existingBookmark || bookmarkSaved ? 'Saved' : 'Bookmark'}
                </button>
              </div>
            </div>

            <div className="space-y-4">
              <h1 className="text-2xl md:text-3xl font-bold text-primary leading-tight">
                {document.title}
              </h1>
              <DocumentMetadata document={document} />
              {document.url && (
                <a
                  href={document.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-sm text-accent hover:underline print:hidden"
                >
                  View on Indian Kanoon
                  <ExternalLink className="w-4 h-4" />
                </a>
              )}
            </div>

            <div className="print:hidden">
              <DocumentSummary
                summary={summaryText}
                isLoading={summaryLoading}
                error={
                  summaryError instanceof Error ? summaryError.message : null
                }
                onGenerate={() => {
                  setSummaryEnabled(true);
                  void refetchSummary();
                }}
              />
            </div>

            {chunkIndex !== null && highlightLoading && (
              <p className="text-sm text-subtext">Loading highlighted passage...</p>
            )}

            <DocumentViewer
              document={document}
              highlightPassage={highlight?.highlighted_passage}
            />
          </>
        )}
      </main>

      {showBookmarkModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 print:hidden">
          <div className="w-full max-w-md bg-white rounded-xl shadow-xl p-6">
            {!isAuthenticated ? (
              <>
                <h3 className="text-lg font-semibold text-primary mb-2">Sign in to bookmark</h3>
                <p className="text-sm text-subtext mb-4">
                  Create an account or log in to save this judgement to your dashboard.
                </p>
                <button
                  type="button"
                  onClick={() => setShowBookmarkModal(false)}
                  className="w-full py-2 text-sm border border-gray-200 rounded-lg"
                >
                  Close
                </button>
              </>
            ) : (
              <>
                <h3 className="text-lg font-semibold text-primary mb-4">Save bookmark</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Folder</label>
                    <select
                      value={bookmarkFolder}
                      onChange={(e) => setBookmarkFolder(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm"
                    >
                      {folders.map((folder) => (
                        <option key={folder} value={folder}>
                          {folder}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Notes (optional)
                    </label>
                    <textarea
                      value={bookmarkNotes}
                      onChange={(e) => setBookmarkNotes(e.target.value)}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm resize-none"
                      placeholder="Why you saved this case..."
                    />
                  </div>
                  {bookmarkError && (
                    <p className="text-sm text-red-600 bg-red-50 border border-red-100 rounded-lg px-3 py-2">
                      {bookmarkError}
                    </p>
                  )}
                  <div className="flex gap-2">
                    <button
                      type="button"
                      onClick={handleSaveBookmark}
                      disabled={isSaving}
                      className="flex-1 py-2 text-sm font-medium text-white bg-accent rounded-lg hover:bg-accent/90 disabled:opacity-60"
                    >
                      {isSaving ? 'Saving...' : 'Save'}
                    </button>
                    <button
                      type="button"
                      onClick={() => setShowBookmarkModal(false)}
                      className="px-4 py-2 text-sm text-subtext"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {showJumpButton && (
        <button
          type="button"
          onClick={handleJumpToHighlight}
          className="fixed bottom-6 right-6 z-20 px-4 py-2.5 bg-primary text-white text-sm font-medium rounded-full shadow-lg hover:bg-primary/90 transition-colors print:hidden"
        >
          Jump to relevant section
        </button>
      )}
    </div>
  );
}
