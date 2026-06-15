import {
  CASE_TYPE_OPTIONS,
  COURT_OPTIONS,
  MAX_YEAR,
  MIN_YEAR,
  OUTCOME_OPTIONS,
  type SearchFilters as SearchFiltersType,
} from '../../types/search.types';

interface SearchFiltersProps {
  filters: SearchFiltersType;
  onChange: (filters: SearchFiltersType) => void;
  onClear: () => void;
}

function toggleValue(list: string[], value: string): string[] {
  return list.includes(value) ? list.filter((item) => item !== value) : [...list, value];
}

export default function SearchFilters({ filters, onChange, onClear }: SearchFiltersProps) {
  return (
    <aside className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-primary">Filters</h2>
        <button
          type="button"
          onClick={onClear}
          className="text-sm text-accent hover:underline"
        >
          Clear Filters
        </button>
      </div>

      <section>
        <h3 className="text-sm font-medium text-primary mb-3">Court</h3>
        <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
          {COURT_OPTIONS.map((court) => (
            <label key={court} className="flex items-start gap-2 text-sm text-subtext cursor-pointer">
              <input
                type="checkbox"
                checked={filters.court.includes(court)}
                onChange={() =>
                  onChange({ ...filters, court: toggleValue(filters.court, court) })
                }
                className="mt-0.5 rounded border-gray-300 text-accent focus:ring-accent"
              />
              <span>{court}</span>
            </label>
          ))}
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-primary mb-3">
          Year range: {filters.year_from ?? MIN_YEAR} – {filters.year_to ?? MAX_YEAR}
        </h3>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-subtext">From</label>
            <input
              type="range"
              min={MIN_YEAR}
              max={MAX_YEAR}
              value={filters.year_from ?? MIN_YEAR}
              onChange={(event) => {
                const yearFrom = Number(event.target.value);
                const yearTo = Math.max(yearFrom, filters.year_to ?? MAX_YEAR);
                onChange({ ...filters, year_from: yearFrom, year_to: yearTo });
              }}
              className="w-full accent-accent"
            />
          </div>
          <div>
            <label className="text-xs text-subtext">To</label>
            <input
              type="range"
              min={MIN_YEAR}
              max={MAX_YEAR}
              value={filters.year_to ?? MAX_YEAR}
              onChange={(event) => {
                const yearTo = Number(event.target.value);
                const yearFrom = Math.min(yearTo, filters.year_from ?? MIN_YEAR);
                onChange({ ...filters, year_from: yearFrom, year_to: yearTo });
              }}
              className="w-full accent-accent"
            />
          </div>
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-primary mb-3">Case Type</h3>
        <div className="space-y-2">
          {CASE_TYPE_OPTIONS.map((caseType) => (
            <label key={caseType} className="flex items-center gap-2 text-sm text-subtext cursor-pointer">
              <input
                type="checkbox"
                checked={filters.case_type.includes(caseType)}
                onChange={() =>
                  onChange({ ...filters, case_type: toggleValue(filters.case_type, caseType) })
                }
                className="rounded border-gray-300 text-accent focus:ring-accent"
              />
              <span>{caseType}</span>
            </label>
          ))}
        </div>
      </section>

      <section>
        <h3 className="text-sm font-medium text-primary mb-3">Outcome</h3>
        <div className="space-y-2">
          <label className="flex items-center gap-2 text-sm text-subtext cursor-pointer">
            <input
              type="radio"
              name="outcome"
              checked={filters.outcome.length === 0}
              onChange={() => onChange({ ...filters, outcome: [] })}
              className="border-gray-300 text-accent focus:ring-accent"
            />
            <span>All outcomes</span>
          </label>
          {OUTCOME_OPTIONS.map((outcome) => (
            <label key={outcome} className="flex items-center gap-2 text-sm text-subtext cursor-pointer">
              <input
                type="radio"
                name="outcome"
                checked={filters.outcome.length === 1 && filters.outcome[0] === outcome}
                onChange={() => onChange({ ...filters, outcome: [outcome] })}
                className="border-gray-300 text-accent focus:ring-accent"
              />
              <span>{outcome}</span>
            </label>
          ))}
        </div>
      </section>
    </aside>
  );
}
