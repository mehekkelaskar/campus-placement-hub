import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { bookmarkAPI } from '../../services/api';
import { Building2, Trash2, ExternalLink, Clock } from 'lucide-react';
import { format } from 'date-fns';

export default function BookmarksPage() {
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchBookmarks = () => {
    setLoading(true);
    bookmarkAPI.list()
      .then((res) => setBookmarks(res.data.results || res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchBookmarks(); }, []);

  const removeBookmark = async (companyId) => {
    try {
      await bookmarkAPI.toggle(companyId);
      setBookmarks(bookmarks.filter((b) => b.company.id !== companyId));
    } catch (err) { console.error(err); }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">My Bookmarks</h1>
        <p className="text-gray-500 text-sm mt-1">Companies you've saved for later</p>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      ) : bookmarks.length === 0 ? (
        <div className="text-center py-16">
          <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No bookmarked companies yet.</p>
          <Link to="/companies" className="text-indigo-600 text-sm mt-2 inline-block hover:underline">
            Browse companies
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {bookmarks.map((bookmark) => {
            const c = bookmark.company;
            return (
              <div key={bookmark.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex items-center gap-4">
                <div className="w-14 h-14 bg-gray-100 rounded-xl flex items-center justify-center flex-shrink-0 overflow-hidden">
                  {c.logo ? (
                    <img src={c.logo} alt={c.name} className="w-full h-full object-contain p-1" />
                  ) : (
                    <Building2 className="w-7 h-7 text-gray-400" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <Link to={`/companies/${c.id}`} className="font-semibold text-gray-900 hover:text-indigo-600 truncate block">
                    {c.name}
                  </Link>
                  <p className="text-sm text-gray-500 truncate">{c.hiring_role}</p>
                  <div className="flex items-center gap-1 text-xs text-gray-400 mt-1">
                    <Clock className="w-3 h-3" />
                    Deadline: {format(new Date(c.deadline), 'MMM dd, yyyy')}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Link
                    to={`/companies/${c.id}`}
                    className="p-2 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition"
                  >
                    <ExternalLink className="w-5 h-5" />
                  </Link>
                  <button
                    onClick={() => removeBookmark(c.id)}
                    className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
