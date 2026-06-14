import { useState } from 'react';
import { Bookmark, History, Settings } from 'lucide-react';
import Navbar from '../components/shared/Navbar';
import Bookmarks from '../components/dashboard/Bookmarks';
import SearchHistory from '../components/dashboard/SearchHistory';
import { useAuth } from '../hooks/useAuth';

type DashboardTab = 'history' | 'bookmarks' | 'settings';

export default function DashboardPage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<DashboardTab>('history');

  const tabs: { id: DashboardTab; label: string; icon: typeof History }[] = [
    { id: 'history', label: 'Search History', icon: History },
    { id: 'bookmarks', label: 'Bookmarks', icon: Bookmark },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-100">
        <Navbar compact />
      </header>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          <aside className="md:col-span-3">
            <div className="bg-white border border-gray-200 rounded-2xl p-5">
              <div className="mb-6">
                <div className="w-12 h-12 rounded-full bg-accent/10 text-accent flex items-center justify-center text-lg font-semibold mb-3">
                  {(user?.full_name || user?.email || '?').charAt(0).toUpperCase()}
                </div>
                <p className="font-semibold text-primary truncate">
                  {user?.full_name || 'User'}
                </p>
                <p className="text-sm text-subtext truncate">{user?.email}</p>
              </div>

              <nav className="space-y-1">
                {tabs.map(({ id, label, icon: Icon }) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setActiveTab(id)}
                    className={`w-full flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                      activeTab === id
                        ? 'bg-accent/10 text-accent font-medium'
                        : 'text-subtext hover:bg-gray-50 hover:text-primary'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {label}
                  </button>
                ))}
              </nav>
            </div>
          </aside>

          <main className="md:col-span-9">
            <div className="bg-white border border-gray-200 rounded-2xl p-6">
              {activeTab === 'history' && <SearchHistory />}
              {activeTab === 'bookmarks' && <Bookmarks />}
              {activeTab === 'settings' && (
                <div>
                  <h2 className="text-xl font-semibold text-primary mb-4">Settings</h2>
                  <p className="text-subtext text-sm">
                    Account settings and preferences will be available in a future update.
                  </p>
                </div>
              )}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
