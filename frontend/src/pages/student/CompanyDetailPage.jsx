import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { companyAPI, bookmarkAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import {
  ArrowLeft, Bookmark, BookmarkCheck, ExternalLink, Globe,
  FileText, Clock, Users, CheckCircle, Calendar, Building2
} from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

export default function CompanyDetailPage() {
  const { id } = useParams();
  const { user } = useAuth();
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [bookmarked, setBookmarked] = useState(false);

  useEffect(() => {
    companyAPI.detail(id)
      .then((res) => {
        setCompany(res.data);
        setBookmarked(res.data.is_bookmarked);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

  const handleBookmark = async () => {
    if (!user) return;
    try {
      const res = await bookmarkAPI.toggle(company.id);
      setBookmarked(res.data.bookmarked);
    } catch (err) { console.error(err); }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600" />
      </div>
    );
  }

  if (!company) return <div className="text-center py-16 text-gray-500">Company not found.</div>;

  const deadlineDate = new Date(company.deadline);
  const isExpired = deadlineDate < new Date();

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Back button */}
      <Link to="/companies" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700">
        <ArrowLeft className="w-4 h-4" />
        Back to Companies
      </Link>

      {/* Hero Card */}
      <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 p-6">
          <div className="flex items-start gap-5">
            <div className="w-20 h-20 bg-white rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg overflow-hidden">
              {company.logo ? (
                <img src={company.logo} alt={company.name} className="w-full h-full object-contain p-2" />
              ) : (
                <Building2 className="w-10 h-10 text-gray-400" />
              )}
            </div>
            <div className="flex-1 text-white">
              <h1 className="text-2xl font-bold">{company.name}</h1>
              <p className="text-indigo-100 mt-1">{company.hiring_role || 'Various Roles'}</p>
              <div className="flex items-center gap-4 mt-3 text-sm text-indigo-100">
                <div className="flex items-center gap-1">
                  <Clock className="w-4 h-4" />
                  <span>{isExpired ? 'Expired' : formatDistanceToNow(deadlineDate, { addSuffix: true })}</span>
                </div>
                <span className="text-indigo-200">|</span>
                <span>{format(deadlineDate, 'MMM dd, yyyy')}</span>
              </div>
            </div>
            {user && (
              <button
                onClick={handleBookmark}
                className={`p-3 rounded-xl transition-colors ${
                  bookmarked ? 'bg-white/20 text-white' : 'bg-white/10 text-white/70 hover:bg-white/20'
                }`}
              >
                {bookmarked ? <BookmarkCheck className="w-6 h-6" /> : <Bookmark className="w-6 h-6" />}
              </button>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex flex-wrap gap-3 p-5 border-b border-gray-100">
          {company.apply_link && (
            <a
              href={company.apply_link}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-700 transition"
            >
              <ExternalLink className="w-4 h-4" />
              Apply Now
            </a>
          )}
          {company.website && (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-gray-100 text-gray-700 px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-200 transition"
            >
              <Globe className="w-4 h-4" />
              Company Website
            </a>
          )}
          {company.jd_pdf && (
            <a
              href={company.jd_pdf}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 bg-gray-100 text-gray-700 px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-200 transition"
            >
              <FileText className="w-4 h-4" />
              Download JD
            </a>
          )}
        </div>
      </div>

      {/* Content Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* About */}
          {company.about && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">About the Company</h2>
              <p className="text-gray-600 text-sm leading-relaxed whitespace-pre-line">{company.about}</p>
            </div>
          )}

          {/* Official Message */}
          {company.official_message && (
            <div className="bg-indigo-50 rounded-xl border border-indigo-100 p-6">
              <h2 className="text-lg font-semibold text-indigo-900 mb-3">Message from Placement Cell</h2>
              <p className="text-indigo-700 text-sm leading-relaxed">{company.official_message}</p>
            </div>
          )}

          {/* Eligibility */}
          {company.eligibility && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-500" />
                Eligibility Criteria
              </h2>
              <p className="text-gray-600 text-sm leading-relaxed whitespace-pre-line">{company.eligibility}</p>
            </div>
          )}

          {/* Recruitment Process */}
          {company.recruitment_process && (
            <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Users className="w-5 h-5 text-blue-500" />
                Recruitment Process
              </h2>
              <p className="text-gray-600 text-sm leading-relaxed whitespace-pre-line">{company.recruitment_process}</p>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          {/* Deadline Card */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <h3 className="font-semibold text-gray-900 mb-3">Key Dates</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Application Deadline</span>
                <span className={`font-medium ${isExpired ? 'text-red-600' : 'text-green-600'}`}>
                  {format(deadlineDate, 'MMM dd, yyyy')}
                </span>
              </div>
              {company.drives?.map((drive) => (
                <div key={drive.id} className="space-y-2 pt-2 border-t border-gray-100">
                  {drive.test_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Online Test</span>
                      <span className="font-medium text-gray-900">
                        {format(new Date(drive.test_date), 'MMM dd, yyyy')}
                      </span>
                    </div>
                  )}
                  {drive.interview_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Interview</span>
                      <span className="font-medium text-gray-900">
                        {format(new Date(drive.interview_date), 'MMM dd, yyyy')}
                      </span>
                    </div>
                  )}
                  {drive.drive_date && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Drive Date</span>
                      <span className="font-medium text-gray-900">
                        {format(new Date(drive.drive_date), 'MMM dd, yyyy')}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Views */}
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 text-center">
            <p className="text-3xl font-bold text-gray-900">{company.views_count}</p>
            <p className="text-sm text-gray-500 mt-1">Total Views</p>
          </div>
        </div>
      </div>
    </div>
  );
}
