import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  Search,
  ShieldAlert,
  Loader2,
  Database,
  Globe,
  Calendar,
} from 'lucide-react';
import { Header } from '../components/Header';
import { watchlistApi } from '../api/client';

export const WatchlistPage = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    handleSearch('');
  }, []);

  const handleSearch = async (searchTerm) => {
    setLoading(true);
    try {
      const data = await watchlistApi.search(searchTerm);
      setResults(data.matches || []);
    } catch (err) {
      console.error('Error querying watchlist:', err);
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = (e) => {
    e.preventDefault();
    handleSearch(query);
  };

  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header
        title="Watchlist & Sanctions Registry"
        subtitle="Database-driven identity blacklist and international alert matching"
      />

      <main className="flex-1 p-6 max-w-[1400px] w-full mx-auto space-y-6">
        {/* Search Bar */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <form onSubmit={onSubmit} className="flex gap-3">
            <div className="relative flex-1">
              <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search database by document number, traveler name, or country..."
                className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-xs text-slate-800 focus:outline-none focus:border-blue-600"
              />
            </div>
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-sm"
            >
              Search Database
            </button>
          </form>
        </div>

        {/* Results List */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-sm">Active Watchlist Entries in Database</h3>
            <span className="text-xs text-slate-400 font-medium">
              Showing {results.length} record(s)
            </span>
          </div>

          {loading ? (
            <div className="p-8 flex justify-center">
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            </div>
          ) : results.length === 0 ? (
            <p className="text-xs text-slate-400 py-6 text-center">No matching records found in database.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {results.map((item) => (
                <div
                  key={item.id}
                  className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-slate-900">{item.name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-50 text-rose-700 border border-rose-200">
                      {item.severity}
                    </span>
                  </div>

                  <div className="space-y-1 text-slate-600 text-[11px]">
                    <p><strong className="text-slate-400">Doc Number:</strong> {item.document_number}</p>
                    <p><strong className="text-slate-400">Nationality:</strong> {item.nationality || 'N/A'}</p>
                    <p><strong className="text-slate-400">Source:</strong> {item.source}</p>
                  </div>

                  <p className="pt-2 border-t border-slate-200/60 text-slate-700 text-[11px] leading-relaxed">
                    {item.reason}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
