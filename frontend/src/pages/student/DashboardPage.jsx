import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dashboardAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { Building2, Calendar, Bookmark, Clock, TrendingUp, ArrowRight } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

export default function DashboardPage() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    dashboardAPI.student()
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

  if (!data) return <div className="text-center text-gray-500 mt-8">Failed to load dashboard data.</div>;

  const stats = [
    { label: 'Total Companies', value: data.stats.total_companies, icon: Building2, color: 'bg-blue-500' },
    { label: 'Upcoming Drives', value: data.stats.upcoming_drives, icon: Calendar, color: 'bg-green-500' },
    { label: 'Bookmarked', value: data.stats.bookmarks, icon: Bookmark, color: 'bg-amber-500' },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.first_name}!
        </h1>
        <p className="text-gray-500 mt-1">Here's what's happening with your placements.</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
        {/* Upcoming Drives */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between p-5 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Upcoming Placement Drives</h2>
            <Link to="/drives" className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="divide-y divide-gray-50">
            {data.upcoming_drives.length === 0 ? (
              <p className="p-5 text-sm text-gray-500">No upcoming drives.</p>
            ) : (
              data.upcoming_drives.map((drive) => (
                <div key={drive.id} className="flex items-center gap-4 p-4 hover:bg-gray-50">
                  <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    {drive.company_logo ? (
                      <img src={drive.company_logo} alt="" className="w-8 h-8 rounded object-contain" />
                    ) : (
                      <Calendar className="w-5 h-5 text-indigo-600" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{drive.company_name}</p>
                    <p className="text-xs text-gray-500">{format(new Date(drive.drive_date), 'MMM dd, yyyy')}</p>
                  </div>
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs font-medium rounded-full">
                    {drive.status}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Recent Companies */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
          <div className="flex items-center justify-between p-5 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900">Recently Added Companies</h2>
            <Link to="/companies" className="text-sm text-indigo-600 hover:text-indigo-700 flex items-center gap-1">
              View all <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="divide-y divide-gray-50">
            {data.recent_companies.length === 0 ? (
              <p className="p-5 text-sm text-gray-500">No companies yet.</p>
            ) : (
              data.recent_companies.map((company) => (
                <Link
                  key={company.id}
                  to={`/companies/${company.id}`}
                  className="flex items-center gap-4 p-4 hover:bg-gray-50"
                >
                  <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
                    {company.logo ? (
                      <img src={company.logo} alt="" className="w-8 h-8 rounded object-contain" />
                    ) : (
                      <Building2 className="w-5 h-5 text-gray-400" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">{company.name}</p>
                    <p className="text-xs text-gray-500 truncate">{company.hiring_role}</p>
                  </div>
                </Link>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Approaching Deadlines */}
      {data.approaching_deadlines.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm">
          <div className="p-5 border-b border-gray-100">
            <h2 className="font-semibold text-gray-900 flex items-center gap-2">
              <Clock className="w-5 h-5 text-amber-500" />
              Approaching Deadlines (Next 7 Days)
            </h2>
          </div>
          <div className="divide-y divide-gray-50">
            {data.approaching_deadlines.map((company) => (
              <Link
                key={company.id}
                to={`/companies/${company.id}`}
                className="flex items-center gap-4 p-4 hover:bg-gray-50"
              >
                <div className="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center flex-shrink-0">
                  <Clock className="w-5 h-5 text-amber-500" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{company.name}</p>
                  <p className="text-xs text-gray-500">{company.hiring_role}</p>
                </div>
                <span className="text-xs font-medium text-amber-600">
                  {formatDistanceToNow(new Date(company.deadline), { addSuffix: true })}
                </span>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
