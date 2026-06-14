import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { AdminStats } from '../../types/dashboard.types';
import { formatDate } from '../../utils/formatDate';

const PROVIDER_COLORS = ['#e94560', '#1a1a2e', '#6366f1', '#10b981'];

interface SearchAnalyticsProps {
  stats: AdminStats;
}

export default function SearchAnalytics({ stats }: SearchAnalyticsProps) {
  const dailyData = stats.searches_per_day.map((item) => ({
    date: item.date.slice(5),
    count: item.count,
  }));

  const topTermsData = stats.top_search_terms.slice(0, 10);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white border border-gray-200 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-primary mb-4">Searches per day (30 days)</h3>
        {dailyData.length ? (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={dailyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line type="monotone" dataKey="count" stroke="#e94560" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-subtext py-12 text-center">No search data yet</p>
        )}
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-primary mb-4">Top search terms</h3>
        {topTermsData.length ? (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={topTermsData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="term"
                width={120}
                tick={{ fontSize: 10 }}
              />
              <Tooltip />
              <Bar dataKey="count" fill="#1a1a2e" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-subtext py-12 text-center">No search terms yet</p>
        )}
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-5 lg:col-span-2">
        <h3 className="text-sm font-semibold text-primary mb-4">Feedback ratings</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div className="p-4 bg-green-50 rounded-xl">
            <p className="text-2xl font-bold text-green-700">{stats.feedback_summary.helpful}</p>
            <p className="text-sm text-green-800">Helpful</p>
          </div>
          <div className="p-4 bg-red-50 rounded-xl">
            <p className="text-2xl font-bold text-red-700">{stats.feedback_summary.not_helpful}</p>
            <p className="text-sm text-red-800">Not helpful</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-xl">
            <p className="text-2xl font-bold text-primary">
              {stats.feedback_summary.helpful_percent}%
            </p>
            <p className="text-sm text-subtext">Helpful rate</p>
          </div>
        </div>
      </div>
    </div>
  );
}

interface ProviderStatsProps {
  stats: AdminStats;
}

export function ProviderStats({ stats }: ProviderStatsProps) {
  const providerData = stats.provider_distribution.map((item) => ({
    name: item.provider,
    value: item.count,
  }));

  return (
    <div className="bg-white border border-gray-200 rounded-2xl p-5">
      <h3 className="text-sm font-semibold text-primary mb-4">Provider usage</h3>
      {providerData.length ? (
        <ResponsiveContainer width="100%" height={280}>
          <PieChart>
            <Pie
              data={providerData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={90}
              label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
            >
              {providerData.map((_, index) => (
                <Cell key={index} fill={PROVIDER_COLORS[index % PROVIDER_COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-sm text-subtext py-12 text-center">No provider data yet</p>
      )}
    </div>
  );
}

interface RecentIssuesProps {
  stats: AdminStats;
}

export function RecentIssues({ stats }: RecentIssuesProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="bg-white border border-gray-200 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-primary mb-4">Recent negative feedback</h3>
        {stats.recent_negative_feedback.length ? (
          <ul className="space-y-3 max-h-72 overflow-y-auto">
            {stats.recent_negative_feedback.map((item, index) => (
              <li key={`${item.query}-${index}`} className="text-sm border-b border-gray-100 pb-2">
                <p className="text-primary line-clamp-2">{item.query}</p>
                <p className="text-xs text-subtext mt-1">
                  {formatDate(item.created_at)}
                  {item.provider_used ? ` · ${item.provider_used}` : ''}
                </p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-subtext">No negative feedback yet</p>
        )}
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl p-5">
        <h3 className="text-sm font-semibold text-primary mb-4">Recent zero-result searches</h3>
        {stats.recent_failed_queries.length ? (
          <ul className="space-y-3 max-h-72 overflow-y-auto">
            {stats.recent_failed_queries.map((item, index) => (
              <li key={`${item.query}-${index}`} className="text-sm border-b border-gray-100 pb-2">
                <p className="text-primary line-clamp-2">{item.query}</p>
                <p className="text-xs text-subtext mt-1">{formatDate(item.failed_at)}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-subtext">No zero-result searches logged</p>
        )}
      </div>
    </div>
  );
}
