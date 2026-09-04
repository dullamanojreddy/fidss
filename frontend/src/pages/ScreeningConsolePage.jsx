import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  CheckCircle2,
  AlertTriangle,
  ShieldCheck,
  ShieldAlert,
  Download,
  ZoomIn,
  ZoomOut,
  Maximize2,
  FileText,
  Calendar,
  Flag,
  User,
  MapPin,
  Clock,
  ArrowRight,
  Eye,
  MoreVertical,
  PlusCircle,
  X,
  Loader2,
  FolderOpen,
} from 'lucide-react';
import { Header } from '../components/Header';
import { screeningApi } from '../api/client';
import OcrOverlay from "../components/OcrOverlay";

export const ScreeningConsolePage = () => {
  const navigate = useNavigate();
  const [screening, setScreening] = useState(null);
  const [recentScreenings, setRecentScreenings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [zoomLevel, setZoomLevel] = useState(1);

  // New Screening Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selfieFile, setSelfieFile] = useState(null);
  const [docType, setDocType] = useState('passport');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const recent = await screeningApi.list(15, 0);
      setRecentScreenings(recent);
      if (recent && recent.length > 0) {
        const active = await screeningApi.getById(recent[0].id);
        setScreening(active);
      } else {
        setScreening(null);
      }
    } catch (err) {
      console.error('Error querying database for screenings:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadSpecificScreening = async (id) => {
    setLoading(true);
    try {
      const data = await screeningApi.getById(id);
      setScreening(data);
    } catch (err) {
      console.error('Error fetching screening detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      setUploadError('Please select a document image to screen.');
      return;
    }

    setUploading(true);
    setUploadError('');

    const formData = new FormData();
    formData.append('document', selectedFile);
    if (selfieFile) {
      formData.append('selfie', selfieFile);
    }
    formData.append('document_type', docType);

    try {
      const newScreening = await screeningApi.create(formData);
      setIsModalOpen(false);
      setSelectedFile(null);
      setSelfieFile(null);
      // Reload screenings list and select the newly created database record
      await loadInitialData();
    } catch (err) {
      console.error('Upload screening failed:', err);
      setUploadError(err.response?.data?.detail || 'Failed to screen document.');
    } finally {
      setUploading(false);
    }
  };

  if (loading && !screening) {
    return (
      <div className="flex-1 flex flex-col">
        <Header title="Screening Console" subtitle="Real-time AI powered document analysis and risk assessment" />
        <div className="flex-1 flex items-center justify-center p-12">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      </div>
    );
  }

  const fields = screening?.extracted_fields || {};
  const isClear = screening?.screening_level === 'CLEAR';
  const riskScore = screening?.overall_risk_score ?? 0;
  const keyFindings = screening?.key_findings || [];
  const moduleResults = screening?.module_results || [];

  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header
        title="Screening Console"
        subtitle="Real-time AI powered document analysis and risk assessment"
      />

      <main className="flex-1 p-6 max-w-[1600px] w-full mx-auto space-y-5">
        {/* Step Progress Stepper */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex items-center justify-between overflow-x-auto">
          {[
            { step: 1, label: 'Upload', status: screening ? 'completed' : 'active' },
            { step: 2, label: 'OCR Extraction', status: screening ? 'completed' : 'pending' },
            { step: 3, label: 'Validation & MRZ', status: screening ? 'completed' : 'pending' },
            { step: 4, label: 'Tampering Analysis', status: screening ? 'completed' : 'pending' },
            { step: 5, label: 'Face Verification', status: screening ? 'completed' : 'pending' },
            { step: 6, label: 'Risk Assessment', status: screening ? (isClear ? 'completed' : 'active') : 'pending' },
            { step: 7, label: 'Completed', status: screening?.status === 'COMPLETED' ? 'completed' : 'pending' },
          ].map((item, idx, arr) => (
            <React.Fragment key={item.step}>
              <div className="flex items-center gap-2 shrink-0">
                <div
                  className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold ${
                    item.status === 'completed'
                      ? 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                      : item.status === 'active'
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'bg-slate-100 text-slate-400 border border-slate-200'
                  }`}
                >
                  {item.status === 'completed' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : (
                    item.step
                  )}
                </div>
                <span
                  className={`text-xs font-medium ${
                    item.status === 'completed'
                      ? 'text-slate-700'
                      : item.status === 'active'
                      ? 'text-blue-700 font-semibold'
                      : 'text-slate-400'
                  }`}
                >
                  {item.label}
                </span>
              </div>
              {idx < arr.length - 1 && (
                <div className="h-0.5 w-8 lg:w-16 bg-slate-200 shrink-0 mx-2" />
              )}
            </React.Fragment>
          ))}
        </div>

        {/* Metadata Strip */}
        <div className="bg-white px-5 py-3.5 rounded-xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-6 text-xs">
            <div>
              <p className="text-slate-400 font-medium">Screening ID</p>
              <p className="font-semibold text-slate-800 mt-0.5">{screening?.screening_number || 'No Active Screening'}</p>
            </div>
            <div className="h-7 w-px bg-slate-200 hidden sm:block" />
            <div>
              <p className="text-slate-400 font-medium">Document Type</p>
              <p className="font-semibold text-slate-800 mt-0.5 capitalize">{screening?.document_type || '—'}</p>
            </div>
            <div className="h-7 w-px bg-slate-200 hidden sm:block" />
            <div>
              <p className="text-slate-400 font-medium">Nationality</p>
              <p className="font-semibold text-slate-800 mt-0.5">{screening?.nationality || '—'}</p>
            </div>
            <div className="h-7 w-px bg-slate-200 hidden sm:block" />
            <div>
              <p className="text-slate-400 font-medium">Submitted By</p>
              <p className="font-semibold text-slate-800 mt-0.5">{screening?.submitted_by || '—'}</p>
            </div>
            <div className="h-7 w-px bg-slate-200 hidden sm:block" />
            <div>
              <p className="text-slate-400 font-medium">Submitted At</p>
              <p className="font-semibold text-slate-800 mt-0.5">
                {screening?.submitted_at
                  ? new Date(screening.submitted_at).toLocaleString()
                  : '—'}
              </p>
            </div>
            <div className="h-7 w-px bg-slate-200 hidden sm:block" />
            <div>
              <p className="text-slate-400 font-medium">Status</p>
              <span className="inline-block mt-0.5 px-2 py-0.5 rounded-full text-[11px] font-semibold bg-blue-50 text-blue-700 border border-blue-200">
                {screening?.status || 'IDLE'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-sm"
            >
              <PlusCircle className="w-3.5 h-3.5" />
              <span>New Screening</span>
            </button>
            <button
              onClick={() => window.print()}
              disabled={!screening}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-blue-700 bg-blue-50 hover:bg-blue-100/70 border border-blue-200 disabled:opacity-50"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Report</span>
            </button>
          </div>
        </div>

        {!screening ? (
          /* Empty State when database contains 0 screenings */
          <div className="bg-white p-12 rounded-2xl border border-slate-200 text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 mx-auto">
              <FolderOpen className="w-8 h-8" />
            </div>
            <h3 className="text-lg font-bold text-slate-900">Database Empty: No Screenings Recorded</h3>
            <p className="text-xs text-slate-500 max-w-md mx-auto leading-relaxed">
              All screening data is purely database driven. Click below to upload and screen your first passport or identity document.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-6 py-2.5 rounded-xl font-bold text-xs text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20"
            >
              Upload Document to Screen
            </button>
          </div>
        ) : (
          /* 3-Column Core Grid Layout */
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            {/* Column 1: Document Preview & Key Findings (4 cols) */}
            <div className="lg:col-span-4 space-y-5">
              {/* Document Preview Card */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-800 text-sm mb-3">Document Preview</h3>
                <div className="relative bg-slate-100 rounded-lg overflow-hidden border border-slate-200 flex items-center justify-center min-h-[260px]">
                  {screening?.document_preview_url ? (
                    <OcrOverlay
                      imageSrc={screening.document_preview_url}
                      rawLines={screening.module_results
                        ?.find((module) => module.module === "ocr")
                        ?.metadata?.raw_lines || []}
                      imageWidth={900}
                      imageHeight={600}
                    />
                  ) : (
                    <div className="text-slate-400 text-xs flex flex-col items-center gap-2">
                      <FileText className="w-8 h-8" />
                      <span>Document Preview</span>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-center gap-4 mt-3 pt-3 border-t border-slate-100 text-xs text-slate-600">
                  <button
                    onClick={() => setZoomLevel((z) => Math.min(z + 0.2, 2.0))}
                    className="flex items-center gap-1 hover:text-blue-600"
                  >
                    <ZoomIn className="w-3.5 h-3.5" />
                    <span>Zoom In</span>
                  </button>
                  <span className="text-slate-300">|</span>
                  <button
                    onClick={() => setZoomLevel((z) => Math.max(z - 0.2, 0.8))}
                    className="flex items-center gap-1 hover:text-blue-600"
                  >
                    <ZoomOut className="w-3.5 h-3.5" />
                    <span>Zoom Out</span>
                  </button>
                  <span className="text-slate-300">|</span>
                  <button
                    onClick={() => setZoomLevel(1)}
                    className="flex items-center gap-1 hover:text-blue-600"
                  >
                    <Maximize2 className="w-3.5 h-3.5" />
                    <span>View Original</span>
                  </button>
                </div>
              </div>

              {/* Key Findings (Evidence) Card */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-800 text-sm mb-3">Key Findings (Evidence)</h3>
                {keyFindings.length === 0 ? (
                  <p className="text-xs text-slate-400 py-4 text-center">No evidence findings recorded in database.</p>
                ) : (
                  <div className="space-y-2.5">
                    {keyFindings.map((item, idx) => (
                      <div key={item.id || idx} className="flex items-center justify-between text-xs py-1">
                        <div className="flex items-center gap-2 min-w-0 pr-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-blue-600 shrink-0"></span>
                          <span className="text-slate-700 font-medium truncate">{item.description}</span>
                        </div>
                        <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-blue-50 text-blue-700 border border-blue-200 shrink-0">
                          {item.severity}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="mt-4 pt-3 border-t border-slate-100">
                  <button
                    onClick={() => navigate('/audit-trail')}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
                  >
                    <span>View Full Evidence List</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            </div>

            {/* Column 2: Overall Risk Assessment & Extracted Fields (4 cols) */}
            <div className="lg:col-span-4 space-y-5">
              {/* Overall Risk Assessment Card */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center text-center">
                <h3 className="font-bold text-slate-800 text-sm w-full text-left mb-4">Overall Risk Assessment</h3>

                <div className="w-16 h-16 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 mb-3 border border-emerald-200">
                  {isClear ? <ShieldCheck className="w-9 h-9" /> : <ShieldAlert className="w-9 h-9 text-amber-600" />}
                </div>

                <h2 className="text-xl font-bold text-slate-900 tracking-tight">{screening?.screening_level}</h2>
                <p className="text-xs font-medium text-slate-500 mb-3">{isClear ? 'Low Risk' : 'Requires Inspection'}</p>

                <div className="text-2xl font-black text-slate-800 mb-2">
                  {riskScore} <span className="text-base text-slate-400 font-normal">/ 100</span>
                </div>

                {/* Gauge Bar */}
                <div className="w-full max-w-xs relative my-2">
                  <div className="h-2.5 w-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-400 to-rose-500" />
                  <div
                    className="absolute top-1/2 -translate-y-1/2 w-4 h-4 rounded-full bg-white border-2 border-emerald-600 shadow-md"
                    style={{ left: `calc(${Math.min(Math.max(riskScore, 2), 98)}% - 8px)` }}
                  />
                </div>

                <p className="text-xs text-slate-500 max-w-xs mt-3 leading-relaxed">
                  {screening?.recommendation_text || 'Automated screening analysis completed.'}
                </p>

                <div className="mt-4 pt-3 border-t border-slate-100 w-full flex items-center justify-between text-xs">
                  <span className="text-slate-400 font-medium">Screening Level</span>
                  <span className="px-2.5 py-0.5 rounded-full font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                    {screening?.screening_level}
                  </span>
                </div>
              </div>

              {/* Document Information (Extracted) Card */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-800 text-sm mb-3">Document Information (Extracted)</h3>
                {Object.keys(fields).length === 0 ? (
                  <p className="text-xs text-slate-400 py-6 text-center">No visual fields extracted from image.</p>
                ) : (
                  <div className="grid grid-cols-2 gap-3 text-xs">
                    {Object.entries(fields).map(([k, v]) => (
                      <div key={k} className="p-2 rounded-lg bg-slate-50 border border-slate-100">
                        <p className="text-slate-400 font-medium text-[11px] truncate">{k}</p>
                        <p className="font-semibold text-slate-800 truncate">{v}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Column 3: Module Results & Next Step (4 cols) */}
            <div className="lg:col-span-4 space-y-5">
              {/* Module Results Card */}
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <h3 className="font-bold text-slate-800 text-sm mb-3">Module Results</h3>
                {moduleResults.length === 0 ? (
                  <p className="text-xs text-slate-400 py-4 text-center">No module executions recorded.</p>
                ) : (
                  <div className="space-y-2">
                    {moduleResults.map((m) => (
                      <div
                        key={m.id || m.module}
                        className="flex items-center justify-between p-2.5 rounded-lg border border-slate-100"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-semibold text-slate-800 uppercase">{m.module}</span>
                          {m.processing_time_ms ? (
                            <span className="text-[10px] text-slate-400">({m.processing_time_ms} ms)</span>
                          ) : null}
                        </div>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                            m.status === 'SUCCESS'
                              ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                              : m.status === 'FAILED'
                              ? 'bg-rose-50 text-rose-700 border border-rose-200'
                              : 'bg-amber-50 text-amber-700 border border-amber-200'
                          }`}
                        >
                          {m.status}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                <div className="mt-4 pt-3 border-t border-slate-100">
                  <button
                    onClick={() => navigate('/audit-trail')}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center justify-between w-full"
                  >
                    <span>View All Evidence ({screening?.total_evidence_count || 0})</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Next Step Card */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex flex-col justify-between">
                <h3 className="font-bold text-slate-800 text-sm mb-3">Next Step</h3>
                <div className="flex items-center gap-4 my-2">
                  <div className="w-14 h-14 rounded-2xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600 shrink-0">
                    <FileText className="w-7 h-7" />
                  </div>
                  <div>
                    <p className="text-xs text-slate-600 font-medium leading-relaxed">
                      Proceed to Officer Review for final decision and notes.
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => navigate('/officer-review')}
                  className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20"
                >
                  <span>Proceed to Review</span>
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Bottom Section: Recent Screenings Table */}
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-slate-800 text-sm">Recent Screenings</h3>
            <span className="text-xs text-slate-400">Total in Database: {recentScreenings.length}</span>
          </div>

          {recentScreenings.length === 0 ? (
            <p className="text-xs text-slate-400 py-6 text-center">No recent screenings in database.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-slate-50 text-slate-400 font-semibold uppercase tracking-wider text-[10px] border-b border-slate-100">
                  <tr>
                    <th className="py-2.5 px-3">Screening ID</th>
                    <th className="py-2.5 px-3">Document Type</th>
                    <th className="py-2.5 px-3">Submitted At</th>
                    <th className="py-2.5 px-3">Risk Level</th>
                    <th className="py-2.5 px-3">Risk Score</th>
                    <th className="py-2.5 px-3">Status</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 text-slate-700">
                  {recentScreenings.map((item) => {
                    const isItemClear = item.screening_level === 'CLEAR';
                    return (
                      <tr key={item.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3 px-3 font-semibold text-slate-900">{item.screening_number}</td>
                        <td className="py-3 px-3">{item.document_type}</td>
                        <td className="py-3 px-3 text-slate-500">{new Date(item.submitted_at).toLocaleString()}</td>
                        <td className="py-3 px-3">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                              isItemClear
                                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                                : 'bg-amber-50 text-amber-700 border border-amber-200'
                            }`}
                          >
                            {item.screening_level}
                          </span>
                        </td>
                        <td className="py-3 px-3 font-bold">{item.overall_risk_score} / 100</td>
                        <td className="py-3 px-3">
                          <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                            {item.status}
                          </span>
                        </td>
                        <td className="py-3 px-3 text-right">
                          <button
                            onClick={() => loadSpecificScreening(item.id)}
                            className="p-1 hover:text-blue-600"
                            title="Inspect Screening"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* New Screening Upload Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-xl border border-slate-200 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="text-base font-bold text-slate-800">New Document Screening</h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {uploadError && (
              <div className="p-3 bg-red-50 text-red-700 rounded-lg text-xs font-medium border border-red-200">
                {uploadError}
              </div>
            )}

            <form onSubmit={handleUploadSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Document Type</label>
                <select
                  value={docType}
                  onChange={(e) => setDocType(e.target.value)}
                  className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-800 focus:outline-none focus:border-blue-600"
                >
                  <option value="passport">Passport</option>
                  <option value="visa">Visa</option>
                  <option value="national_id">National ID</option>
                  <option value="driving_license">Driving License</option>
                </select>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Document Image <span className="text-red-500">*</span>
                </label>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-300 rounded-lg p-1.5"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Optional Traveler Selfie (for Face Verification)
                </label>
                <input
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={(e) => setSelfieFile(e.target.files[0])}
                  className="w-full text-xs text-slate-500 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-slate-100 file:text-slate-700 hover:file:bg-slate-200 cursor-pointer border border-slate-300 rounded-lg p-1.5"
                />
              </div>

              <div className="pt-3 border-t border-slate-100 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-lg font-semibold text-slate-600 hover:bg-slate-100"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={uploading}
                  className="px-5 py-2 rounded-lg font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-sm flex items-center gap-2 disabled:opacity-50"
                >
                  {uploading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin" />
                      <span>Executing 12-Step Pipeline...</span>
                    </>
                  ) : (
                    <span>Start Screening</span>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
