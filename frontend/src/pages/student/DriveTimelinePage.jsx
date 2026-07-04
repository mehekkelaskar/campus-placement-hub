import { useState, useEffect } from 'react';
import { driveAPI } from '../../services/api';
import { Calendar, Building2, MapPin } from 'lucide-react';
import { format } from 'date-fns';

export default function DriveTimelinePage() {
  const [drives, setDrives] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    driveAPI.list(filter ? { status: filter } : {})
      .then((res) => setDrives(res.data.results || res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [filter]);

  const statusColors = {
    upcoming: 'bg-green-100 text-green-700 border-green-200',
    ongoing: 'bg-blue-100 text-blue-700 border-blue-200',
    closed: 'bg-gray-100 text-gray-600 border-gray-200',
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Placement Drive Timeline</h1>
          <p className="text-gray-500 text-sm mt-1">Track upcoming, ongoing, and closed placement drives</p>
        </div>
        <div className="flex gap-2">
          {['', 'upcoming', 'ongoing', 'closed'].map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                filter === s ? 'bg-indigo-600 text-white' : 'bg-white text-gray-600 hover:bg-gray-50 border border-gray-200'
              }`}
            >
              {s || 'All'}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
        </div>
      ) : drives.length === 0 ? (
        <div className="text-center py-16">
          <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No drives found.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {drives.map((drive) => (
            <div key={drive.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center flex-shrink-0">
                  <Calendar className="w-6 h-6 text-indigo-600" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="font-semibold text-gray-900">{drive.company}</h3>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${statusColors[drive.status] || ''}`}>
                      {drive.status}
                    </span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-sm">
                    <div className="flex items-center gap-2 text-gray-500">
                      <MapPin className="w-4 h-4 text-blue-400" />
                      <span>Drive: {format(new Date(drive.drive_date), 'MMM dd, yyyy')}</span>
                    </div>
                    {drive.test_date && (
                      <div className="flex items-center gap-2 text-gray-500">
                        <Calendar className="w-4 h-4 text-purple-400" />
                        <span>Test: {format(new Date(drive.test_date), 'MMM dd, yyyy')}</span>
                      </div>
                    )}
                    {drive.interview_date && (
                      <div className="flex items-center gap-2 text-gray-500">
                        <Building2 className="w-4 h-4 text-green-400" />
                        <span>Interview: {format(new Date(drive.interview_date), 'MMM dd, yyyy')}</span>
                      </div>
                    )}
                  </div>
                  {drive.notes && (
                    <p className="mt-3 text-sm text-gray-500 bg-gray-50 rounded-lg p-3">{drive.notes}</p>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
