import React, { useState, useEffect } from 'react';
import { Files, Eye, Download, Search, Loader2 } from 'lucide-react';
import { Header } from '../components/Header';
import { screeningApi } from '../api/client';
import { useNavigate } from 'react-router-dom';

export const DocumentsPage = () => {
  const navigate = useNavigate();
  const [screenings, setScreenings] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadScreenings();
  }, []);

  const loadScreenings = async () => {
    setLoading(true);
    try {
      const data = await screeningApi.list(50, 0);
      setScreenings(data);
    } catch (err) {
      console.error('Error fetching documents:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header
        title="Document Repository"
        subtitle="Archived document scans, cryptographic hashes, and screening results"
      />

      <main className="flex-1 p-6 max-w-[1400px] w-full mx-auto space-y-6">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-900 text-sm">Archived Documents</h3>
            <span className="text-xs text-slate-400">Total: {screenings.length} document(s)</span>
          </div>

          {loading ? (
            <div className="p-8 flex justify-center">
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-400 uppercase text-[10px] font-semibold border-b border-slate-100">
                  <tr>
                    <th className="py-2.5 px-3">Screening ID</th>
                    <th className="py-2.5 px-3">Document Type</th>
                    <th className="py-2.5 px-3">Timestamp</th>
                    <th className="py-2.5 px-3">Screening Level</th>
                    <th className="py-2.5 px-3">Risk Score</th>
                    <th className="py-2.5 px-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {screenings.map((s) => (
                    <tr key={s.id} className="hover:bg-slate-50/80">
                      <td className="py-3 px-3 font-semibold text-slate-900">{s.screening_number}</td>
                      <td className="py-3 px-3">{s.document_type}</td>
                      <td className="py-3 px-3 text-slate-500">{new Date(s.submitted_at).toLocaleString()}</td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700">
                          {s.screening_level}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-bold">{s.overall_risk_score} / 100</td>
                      <td className="py-3 px-3 text-right">
                        <button
                          onClick={() => navigate('/screening-console')}
                          className="px-2.5 py-1 rounded bg-blue-50 text-blue-700 hover:bg-blue-100 text-xs font-semibold"
                        >
                          View in Console
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
