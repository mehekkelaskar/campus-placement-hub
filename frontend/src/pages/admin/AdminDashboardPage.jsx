import { useState, useEffect } from 'react';
import { dashboardAPI } from '../../services/api';
import { Building2, Users, Calendar, Bookmark, TrendingUp, Eye } from 'lucide-react';

export default function AdminDashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.admin()
      .then((res) => setData(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (!data) return <div className="text-center text-gray-500 mt-8">Failed to load dashboard.</div>;

  const stats = [
    { label: 'Total Companies', value: data.stats.total_companies, icon: Building2, color: 'bg-blue-500' },
    { label: 'Published', value: data.stats.published_companies, icon: Eye, color: 'bg-green-500' },
    { label: 'Total Students', value: data.stats.total_students, icon: Users, color: 'bg-purple-500' },
    { label: 'Verified Students', value: data.stats.verified_students, icon: Users, color: 'bg-indigo-500' },
    { label: 'Active Drives', value: data.stats.active_drives, icon: Calendar, color: 'bg-amber-500' },
    { label: 'Total Bookmarks', value: data.stats.total_bookmarks, icon: Bookmark, color: 'bg-pink-500' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of the placement portal</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white rounded-xl p-5 border border-gray-100 shadow-sm">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={`w-12 h-12 ${stat.color} rounded-xl flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Bookmarked */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
          <div className="p-5 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <Bookmark className="w-5 h-5 text-pink-500" />
              Most Bookmarked Companies
            </h2>
          </div>
          <div className="divide-y divide-gray-50">
            {data.most_bookmarked.length === 0 ? (
              <p className="p-5 text-sm text-gray-500">No data yet.</p>
            ) : (
              data.most_bookmarked.map((c, i) => (
                <div key={c.id} className="flex items-center gap-4 p-4">
                  <span className="w-8 h-8 bg-pink-50 rounded-lg flex items-center justify-center text-sm font-bold text-pink-600">
                    {i + 1}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{c.name}</p>
                  </div>
                  <span className="text-sm font-semibold text-pink-600">{c.bookmark_count}</span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Most Viewed */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
          <div className="p-5 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <Eye className="w-5 h-5 text-blue-500" />
              Most Viewed Companies
            </h2>
          </div>
          <div className="divide-y divide-gray-50">
            {data.most_viewed.length === 0 ? (
              <p className="p-5 text-sm text-gray-500">No data yet.</p>
            ) : (
              data.most_viewed.map((c, i) => (
                <div key={c.id} className="flex items-center gap-4 p-4">
                  <span className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center text-sm font-bold text-blue-600">
                    {i + 1}
                  </span>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{c.name}</p>
                  </div>
                  <span className="text-sm font-semibold text-blue-600">{c.views_count} views</span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
