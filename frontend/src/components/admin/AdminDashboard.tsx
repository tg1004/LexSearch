import { Activity, BarChart3, Clock, Search } from 'lucide-react';
import type { AdminStats } from '../../types/dashboard.types';
import SearchAnalytics, { ProviderStats, RecentIssues } from './SearchAnalytics';

interface AdminDashboardProps {
  stats: AdminStats;
}

export default function AdminDashboard({ stats }: AdminDashboardProps) {
  const metrics = [
    {
      label: 'Searches today',
      value: stats.searches_today,
      icon: Search,
    },
    {
      label: 'Searches this week',
      value: stats.searches_this_week,
      icon: BarChart3,
    },
    {
      label: 'Avg response time',
      value: stats.avg_response_time_ms ? `${stats.avg_response_time_ms}ms` : 'N/A',
      icon: Clock,
    },
    {
      label: 'Helpful feedback',
      value: `${stats.feedback_summary.helpful_percent}%`,
      icon: Activity,
    },
  ];

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map(({ label, value, icon: Icon }) => (
          <div
            key={label}
            className="bg-white border border-gray-200 rounded-2xl p-5"
          >
            <div className="flex items-center justify-between mb-3">
              <p className="text-sm text-subtext">{label}</p>
              <Icon className="w-5 h-5 text-accent" />
            </div>
            <p className="text-2xl font-bold text-primary">{value}</p>
          </div>
        ))}
      </div>

      <SearchAnalytics stats={stats} />

      <ProviderStats stats={stats} />

      <RecentIssues stats={stats} />
    </div>
  );
}
