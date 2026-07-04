import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { companyAPI, bookmarkAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { Search, SlidersHorizontal, Building2, Bookmark, BookmarkCheck, Clock, ExternalLink } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

export default function CompaniesPage() {
  const { user } = useAuth();
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [sort, setSort] = useState('latest');
  const [statusFilter, setStatusFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  const fetchCompanies = () => {
    setLoading(true);
    companyAPI.list({ search, sort, status: statusFilter, page })
      .then((res) => {
        setCompanies(res.data.results || res.data);
        if (res.data.count) {
          setTotalPages(Math.ceil(res.data.count / 12));
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchCompanies(); }, [search, sort, statusFilter, page]);

  const handleBookmark = async (e, companyId) => {
    e.preventDefault();
    e.stopPropagation();
    if (!user) return;
    try {
      await bookmarkAPI.toggle(companyId);
      fetchCompanies();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Placement Companies</h1>
          <p className="text-gray-500 text-sm mt-1">Browse and bookmark companies visiting campus</p>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search companies..."
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="w-full pl-11 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-transparent outline-none text-sm"
            />
          </div>
          <select
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
            className="px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
          >
            <option value="">All Status</option>
            <option value="upcoming">Upcoming</option>
            <option value="ongoing">Ongoing</option>
            <option value="closed">Closed</option>
          </select>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="px-4 py-2.5 border border-gray-200 rounded-xl text-sm focus:ring-2 focus:ring-indigo-500 outline-none bg-white"
          >
            <option value="latest">Latest First</option>
            <option value="deadline">By Deadline</option>
            <option value="name">Name A-Z</option>
          </select>
        </div>
      </div>

      {/* Company Grid */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      ) : companies.length === 0 ? (
        <div className="text-center py-16">
          <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No companies found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {companies.map((company) => (
            <Link
              key={company.id}
              to={`/companies/${company.id}`}
              className="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow p-5 group"
            >
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 bg-gray-100 rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden">
                  {company.logo ? (
                    <img src={company.logo} alt={company.name} className="w-full h-full object-contain p-1" />
                  ) : (
                    <Building2 className="w-7 h-7 text-gray-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600 transition-colors truncate">
                    {company.name}
                  </h3>
                  <p className="text-sm text-gray-500 truncate mt-0.5">{company.hiring_role || 'Various Roles'}</p>
                </div>
                {user && (
                  <button
                    onClick={(e) => handleBookmark(e, company.id)}
                    className="p-1.5 hover:bg-gray-100 rounded-lg transition-colors"
                    title="Toggle bookmark"
                  >
                    <Bookmark className="w-5 h-5 text-gray-400 hover:text-indigo-600" />
                  </button>
                )}
              </div>

              <div className="mt-4 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1 text-gray-500">
                  <Clock className="w-3.5 h-3.5" />
                  <span>Deadline: {format(new Date(company.deadline), 'MMM dd, yyyy')}</span>
                </div>
                {company.drive_status && (
                  <span className={`px-2 py-0.5 rounded-full font-medium ${
                    company.drive_status === 'upcoming' ? 'bg-green-100 text-green-700' :
                    company.drive_status === 'ongoing' ? 'bg-blue-100 text-blue-700' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    {company.drive_status}
                  </span>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                p === page ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
