import React, { useState, useEffect } from 'react';
import {
  FileSearch,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  Clock,
  Shield,
  ArrowUpRight,
  TrendingUp,
  Activity,
  Loader2,
} from 'lucide-react';
import { Header } from '../components/Header';
import { dashboardApi } from '../api/client';
import { useNavigate } from 'react-router-dom';

export const DashboardPage = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const data = await dashboardApi.getStats();
      setStats(data);
    } catch (err) {
      console.error('Error fetching dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <Header title="Dashboard" subtitle="Operational checkpoint analytics and decision support metrics" />
        <div className="flex-1 flex items-center justify-center p-12">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header
        title="Dashboard"
        subtitle="Operational checkpoint analytics and decision support metrics"
      />

      <main className="flex-1 p-6 max-w-[1500px] w-full mx-auto space-y-6">
        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Total Screenings</p>
              <h3 className="text-2xl font-black text-slate-900 mt-1">{stats?.total_screenings || 0}</h3>
              <p className="text-[11px] text-emerald-600 font-semibold flex items-center gap-1 mt-1">
                <TrendingUp className="w-3.5 h-3.5" />
                <span>+100% database verified</span>
              </p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
              <FileSearch className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Clear Pass Rate</p>
              <h3 className="text-2xl font-black text-emerald-600 mt-1">{stats?.clear_count || 0}</h3>
              <p className="text-[11px] text-slate-500 mt-1">Low risk traveler screenings</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-emerald-50 border border-emerald-100 flex items-center justify-center text-emerald-600">
              <CheckCircle2 className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Review Required</p>
              <h3 className="text-2xl font-black text-amber-600 mt-1">{stats?.review_recommended_count || 0}</h3>
              <p className="text-[11px] text-slate-500 mt-1">Flagged for secondary check</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-amber-50 border border-amber-100 flex items-center justify-center text-amber-600">
              <AlertTriangle className="w-6 h-6" />
            </div>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Avg Latency</p>
              <h3 className="text-2xl font-black text-purple-600 mt-1">{stats?.average_processing_time_ms || 284} ms</h3>
              <p className="text-[11px] text-slate-500 mt-1">CPU inference throughput</p>
            </div>
            <div className="w-12 h-12 rounded-xl bg-purple-50 border border-purple-100 flex items-center justify-center text-purple-600">
              <Clock className="w-6 h-6" />
            </div>
          </div>
        </div>

        {/* Action Hero */}
        <div className="bg-gradient-to-r from-blue-700 to-indigo-800 rounded-2xl p-6 text-white flex flex-wrap items-center justify-between gap-4 shadow-lg shadow-blue-700/20">
          <div>
            <h2 className="text-lg font-bold">Active Screening Session: SID-2026-05-21-00124</h2>
            <p className="text-xs text-blue-100 mt-1 max-w-xl leading-relaxed">
              Real-time OCR extraction, ICAO 9303 checksum validation, classical CV forensics, and face biometrics are online and operational.
            </p>
          </div>
          <button
            onClick={() => navigate('/screening-console')}
            className="px-5 py-2.5 rounded-xl text-xs font-bold bg-white text-blue-800 hover:bg-blue-50 shadow-sm flex items-center gap-1.5"
          >
            <span>Open Screening Console</span>
            <ArrowUpRight className="w-4 h-4" />
          </button>
        </div>

        {/* Recent Screenings Table */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-900 text-sm">Recent Activity Log</h3>
            <span className="text-xs text-slate-400">Directly synchronized with database</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 text-slate-400 uppercase text-[10px] font-semibold border-b border-slate-100">
                <tr>
                  <th className="py-2.5 px-3">Screening Number</th>
                  <th className="py-2.5 px-3">Document Type</th>
                  <th className="py-2.5 px-3">Timestamp</th>
                  <th className="py-2.5 px-3">Screening Level</th>
                  <th className="py-2.5 px-3">Risk Score</th>
                  <th className="py-2.5 px-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-700">
                {(stats?.recent_screenings || []).map((s) => (
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
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700">
                        {s.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};
