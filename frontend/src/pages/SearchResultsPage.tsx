import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import AIAnswer from '../components/results/AIAnswer';
import RelatedQuestions from '../components/results/RelatedQuestions';
import SearchResultsSkeleton from '../components/results/SearchResultsSkeleton';
import SourceCard from '../components/results/SourceCard';
import ModelSelector from '../components/search/ModelSelector';
import SearchBar from '../components/search/SearchBar';
import SearchFilters from '../components/search/SearchFilters';
import ErrorMessage from '../components/shared/ErrorMessage';
import Navbar from '../components/shared/Navbar';
import { useProviders } from '../hooks/useProviders';
import { useSearch } from '../hooks/useSearch';
import { usePreferencesStore } from '../store/preferencesStore';
import { EMPTY_FILTERS, useSearchStore } from '../store/searchStore';
import type { PreferredProvider, SearchFilters as SearchFiltersType } from '../types/search.types';
import { MAX_YEAR, MIN_YEAR } from '../types/search.types';
import { debounce } from '../utils/debounce';

function parseListParam(value: string | null): string[] {
  if (!value) return [];
  return value.split(',').map((item) => item.trim()).filter(Boolean);
}

function parseFiltersFromParams(params: URLSearchParams): SearchFiltersType {
  const yearFrom = Number(params.get('year_from'));
  const yearTo = Number(params.get('year_to'));

  return {
    court: parseListParam(params.get('court')),
    case_type: parseListParam(params.get('case_type')),
    outcome: parseListParam(params.get('outcome')),
    year_from: Number.isFinite(yearFrom) && yearFrom > 0 ? yearFrom : MIN_YEAR,
    year_to: Number.isFinite(yearTo) && yearTo > 0 ? yearTo : MAX_YEAR,
  };
}

function buildSearchParams(
  query: string,
  filters: SearchFiltersType,
  provider: PreferredProvider,
): URLSearchParams {
  const params = new URLSearchParams();
  params.set('q', query);

  if (provider !== 'auto') {
    params.set('provider', provider);
  }

  if (filters.court.length) {
    params.set('court', filters.court.join(','));
  }

  if (filters.case_type.length) {
    params.set('case_type', filters.case_type.join(','));
  }

  if (filters.outcome.length) {
    params.set('outcome', filters.outcome.join(','));
  }

  if (filters.year_from !== undefined && filters.year_from > MIN_YEAR) {
    params.set('year_from', String(filters.year_from));
  }

  if (filters.year_to !== undefined && filters.year_to < MAX_YEAR) {
    params.set('year_to', String(filters.year_to));
  }

  return params;
}

export default function SearchResultsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { preferredProvider, setPreferredProvider } = usePreferencesStore();
  const { setFilters, resetFilters } = useSearchStore();

  const queryFromUrl = searchParams.get('q') ?? '';
  const providerFromUrl = (searchParams.get('provider') as PreferredProvider | null) ?? preferredProvider;
  const filtersFromUrl = useMemo(
    () => parseFiltersFromParams(searchParams),
    [searchParams],
  );

  const [draftQuery, setDraftQuery] = useState(queryFromUrl);
  const [draftFilters, setDraftFilters] = useState(filtersFromUrl);

  useEffect(() => {
    setDraftQuery(queryFromUrl);
  }, [queryFromUrl]);

  useEffect(() => {
    setDraftFilters(filtersFromUrl);
  }, [filtersFromUrl]);

  useEffect(() => {
    setFilters(filtersFromUrl);
  }, [filtersFromUrl, setFilters]);

  useEffect(() => {
    if (providerFromUrl) {
      setPreferredProvider(providerFromUrl);
    }
  }, [providerFromUrl, setPreferredProvider]);

  const { data: providersData, isLoading: providersLoading } = useProviders();
  const {
    data,
    isLoading,
    isFetching,
    error,
    refetch,
  } = useSearch({
    query: queryFromUrl,
    preferredProvider: providerFromUrl,
    filters: filtersFromUrl,
    enabled: queryFromUrl.trim().length > 0,
  });

  const maxScore = useMemo(
    () => Math.max(0, ...(data?.sources.map((source) => source.score) ?? [])),
    [data?.sources],
  );

  const providerModel = useMemo(() => {
    if (!data?.provider_used || !providersData?.providers) return null;
    return providersData.providers.find((provider) => provider.name === data.provider_used)?.model ?? null;
  }, [data?.provider_used, providersData?.providers]);

  const showFallbackWarning =
    providerFromUrl !== 'auto' &&
    !!data?.provider_used &&
    data.provider_used !== providerFromUrl;

  const isUnavailableAnswer =
    data?.answer === 'Service temporarily unavailable, please try again.';
  const isEmptyResults =
    !!data &&
    data.result_count === 0 &&
    data.answer.startsWith('No results found');

  const runSearch = useCallback((
    nextQuery: string,
    nextFilters: SearchFiltersType = filtersFromUrl,
    nextProvider: PreferredProvider = providerFromUrl,
  ) => {
    const trimmed = nextQuery.trim();
    if (!trimmed) return;

    const params = buildSearchParams(trimmed, nextFilters, nextProvider);
    setSearchParams(params);
  }, [filtersFromUrl, providerFromUrl, setSearchParams]);

  const debouncedFilterSearch = useMemo(
    () => debounce((nextFilters: SearchFiltersType) => {
      runSearch(queryFromUrl, nextFilters);
    }, 500),
    [queryFromUrl, runSearch],
  );

  useEffect(() => () => debouncedFilterSearch.cancel?.(), [debouncedFilterSearch]);

  const handleCitationClick = (number: number) => {
    const element = document.getElementById(`source-${number}`);
    element?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  if (!queryFromUrl.trim()) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center px-6 text-center">
        <p className="text-lg text-primary mb-4">Enter a search query to get started.</p>
        <Link to="/" className="text-accent hover:underline">
          Back to home
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center gap-4 px-4 sm:px-6 py-3 border-b border-gray-50 lg:border-0">
            <div className="flex-1 min-w-0">
              <SearchBar
                value={draftQuery}
                onChange={setDraftQuery}
                onSubmit={() => runSearch(draftQuery)}
                compact
              />
            </div>
          </div>
          <Navbar compact />
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className="lg:col-span-3">
            <div className="bg-white border border-gray-200 rounded-2xl p-5 lg:sticky lg:top-6">
              <SearchFilters
                filters={draftFilters}
                onChange={(nextFilters) => {
                  setDraftFilters(nextFilters);
                  debouncedFilterSearch(nextFilters);
                }}
                onClear={() => {
                  resetFilters();
                  setDraftFilters({ ...EMPTY_FILTERS });
                  runSearch(queryFromUrl, { ...EMPTY_FILTERS });
                }}
              />
            </div>
          </div>

          <div className="lg:col-span-9 space-y-6">
            <ModelSelector
              providers={providersData?.providers ?? []}
              selected={providerFromUrl}
              onChange={(provider) => {
                setPreferredProvider(provider);
                runSearch(queryFromUrl, filtersFromUrl, provider);
              }}
              isLoading={providersLoading}
            />

            {error && (
              <ErrorMessage
                message={
                  error instanceof Error
                    ? error.message
                    : 'Search failed. Please try again.'
                }
              />
            )}

            {(isLoading || (isFetching && !data)) && <SearchResultsSkeleton />}

            {data && !isLoading && (
              <>
                {isEmptyResults ? (
                  <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center">
                    <h2 className="text-xl font-semibold text-primary mb-2">
                      No results found for this query
                    </h2>
                    <p className="text-subtext mb-4">
                      Try broader terms, check spelling, or remove filters.
                    </p>
                    <button
                      type="button"
                      onClick={() => {
                        resetFilters();
                        setDraftFilters({ ...EMPTY_FILTERS });
                        runSearch(queryFromUrl, { ...EMPTY_FILTERS });
                      }}
                      className="text-sm text-accent hover:underline"
                    >
                      Clear all filters
                    </button>
                  </div>
                ) : (
                  <>
                    <AIAnswer
                      answer={data.answer}
                      citations={data.citations}
                      providerUsed={data.provider_used}
                      providerModel={providerModel}
                      searchId={data.search_id}
                      query={queryFromUrl}
                      preferredProvider={providerFromUrl}
                      onCitationClick={handleCitationClick}
                      isUnavailable={isUnavailableAnswer}
                      showFallbackWarning={showFallbackWarning}
                      fallbackFrom={providerFromUrl}
                    />

                    <RelatedQuestions
                      questions={data.related_questions}
                      onSelect={(question) => runSearch(question)}
                    />

                    <section>
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-primary">
                          Sources
                        </h2>
                        <span className="text-sm text-subtext">
                          {data.result_count} result{data.result_count === 1 ? '' : 's'}
                        </span>
                      </div>

                      <div className="space-y-4">
                        {data.sources.map((source, index) => (
                          <SourceCard
                            key={`${source.document_id}-${source.chunk_index ?? index}`}
                            id={`source-${index + 1}`}
                            source={source}
                            index={index + 1}
                            query={queryFromUrl}
                            maxScore={maxScore}
                          />
                        ))}
                      </div>
                    </section>
                  </>
                )}
              </>
            )}

            {data && isFetching && !isLoading && (
              <p className="text-sm text-subtext">Refreshing results...</p>
            )}

            {error && (
              <button
                type="button"
                onClick={() => refetch()}
                className="text-sm text-accent hover:underline"
              >
                Retry search
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
