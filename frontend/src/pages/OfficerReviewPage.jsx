import React, { useState, useEffect } from 'react';
import {
  UserCheck,
  CheckCircle2,
  XCircle,
  AlertOctagon,
  RefreshCw,
  HelpCircle,
  ShieldCheck,
  FileText,
  Loader2,
  ArrowLeft,
  Check,
} from 'lucide-react';
import { Header } from '../components/Header';
import { screeningApi } from '../api/client';
import { useNavigate, useParams } from 'react-router-dom';

const DECISIONS = [
  { id: 'ACCEPT', label: 'Accept & Clear', icon: CheckCircle2, color: 'bg-emerald-600 hover:bg-emerald-700 text-white', border: 'border-emerald-600' },
  { id: 'REJECT', label: 'Reject Entry', icon: XCircle, color: 'bg-rose-600 hover:bg-rose-700 text-white', border: 'border-rose-600' },
  { id: 'ESCALATE', label: 'Escalate to Secondary', icon: AlertOctagon, color: 'bg-amber-600 hover:bg-amber-700 text-white', border: 'border-amber-600' },
  { id: 'REQUEST_RECAPTURE', label: 'Request Recapture', icon: RefreshCw, color: 'bg-blue-600 hover:bg-blue-700 text-white', border: 'border-blue-600' },
  { id: 'MARK_INCONCLUSIVE', label: 'Mark Inconclusive', icon: HelpCircle, color: 'bg-slate-600 hover:bg-slate-700 text-white', border: 'border-slate-600' },
];

export const OfficerReviewPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const [screening, setScreening] = useState(null);
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [selectedDecision, setSelectedDecision] = useState('ACCEPT');
  const [reason, setReason] = useState('VALIDATED_CREDENTIALS');
  const [notes, setNotes] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    loadReviewData();
  }, [id]);

  const loadReviewData = async () => {
    setLoading(true);
    try {
      let targetId = id;
      if (!targetId) {
        const recent = await screeningApi.list(1, 0);
        if (recent && recent.length > 0) {
          targetId = recent[0].id;
        }
      }
      if (!targetId) {
        setScreening(null);
        return;
      }
      const data = await screeningApi.getById(targetId);
      setScreening(data);
      const ev = await screeningApi.getEvidence(data.id);
      setEvidenceList(ev);

      // Check if existing review
      const existing = await screeningApi.getReview(data.id);
      if (existing) {
        setSelectedDecision(existing.decision);
        setReason(existing.reason);
        setNotes(existing.notes || '');
      }
    } catch (err) {
      console.error('Error fetching review data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!screening) return;
    setSubmitting(true);
    try {
      await screeningApi.submitReview(screening.id, {
        decision: selectedDecision,
        reason,
        notes,
      });
      setSuccessMessage('Officer review recorded and cryptographically logged to audit trail.');
      setTimeout(() => setSuccessMessage(''), 4000);
    } catch (err) {
      console.error('Error submitting review:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 flex flex-col">
        <Header title="Officer Review" subtitle="Human-in-the-loop operational decision recording" />
        <div className="flex-1 flex items-center justify-center p-12">
          <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header title="Officer Review" subtitle="Human-in-the-loop operational decision recording" />

      <main className="flex-1 p-6 max-w-[1400px] w-full mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/screening-console')}
            className="flex items-center gap-2 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white px-3 py-1.5 rounded-lg border border-slate-200"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Console</span>
          </button>
          <span className="text-xs text-slate-400 font-medium">
            Screening Ref: <strong className="text-slate-700">{screening?.screening_number}</strong>
          </span>
        </div>

        {successMessage && (
          <div className="p-4 bg-emerald-50 text-emerald-800 rounded-xl border border-emerald-200 text-xs font-semibold flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-600" />
            <span>{successMessage}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Evidence Summary & Document Reference (5 cols) */}
          <div className="lg:col-span-5 space-y-5">
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-3">Document & Biometric Summary</h3>
              <div className="bg-slate-100 rounded-lg overflow-hidden border border-slate-200 p-2 flex items-center justify-center mb-4">
                <img
                  src={screening?.document_preview_url || '/static/uploads/demo_passport.png'}
                  alt="Document"
                  className="max-h-48 object-contain rounded"
                />
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-400">Automated Recommendation</span>
                  <span className="font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                    {screening?.screening_level}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-400">Calculated Risk Score</span>
                  <span className="font-bold text-slate-800">{screening?.overall_risk_score} / 100</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-400">Traveler Name</span>
                  <span className="font-semibold text-slate-800">
                    {screening?.extracted_fields?.['Given Name']} {screening?.extracted_fields?.['Surname']}
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Document Number</span>
                  <span className="font-semibold text-slate-800">{screening?.extracted_fields?.['Passport Number']}</span>
                </div>
              </div>
            </div>

            {/* Granular Evidence Items */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-3">Supporting Evidence Findings</h3>
              <div className="space-y-2.5 max-h-72 overflow-y-auto pr-1">
                {evidenceList.map((ev) => (
                  <div key={ev.id} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-slate-800">{ev.category}</span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded font-bold bg-blue-50 text-blue-700">
                        {ev.severity}
                      </span>
                    </div>
                    <p className="text-slate-600 text-[11px] leading-relaxed">{ev.description}</p>
                    <div className="mt-1.5 flex items-center justify-between text-[10px] text-slate-400">
                      <span>Source: {ev.source}</span>
                      <span>Confidence: {(ev.confidence * 100).toFixed(1)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column: Officer Decision Controls Form (7 cols) */}
          <div className="lg:col-span-7">
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-base font-bold text-slate-900 mb-1">Record Operational Decision</h3>
              <p className="text-xs text-slate-500 mb-5">
                The automated system provides decision support. The authorized border officer renders the legal determination.
              </p>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Decision Selector Buttons */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-2">Operational Decision</label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {DECISIONS.map((d) => {
                      const Icon = d.icon;
                      const isSelected = selectedDecision === d.id;
                      return (
                        <button
                          key={d.id}
                          type="button"
                          onClick={() => setSelectedDecision(d.id)}
                          className={`flex items-center gap-2.5 p-3 rounded-xl text-xs font-bold border transition-all text-left ${
                            isSelected
                              ? `${d.color} shadow-sm ring-2 ring-offset-1 ring-blue-500`
                              : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                          }`}
                        >
                          <Icon className="w-4 h-4 shrink-0" />
                          <span>{d.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Justification Reason Code */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Reason Code</label>
                  <select
                    value={reason}
                    onChange={(e) => setReason(e.target.value)}
                    className="w-full border border-slate-300 rounded-lg p-2.5 text-xs text-slate-800 focus:outline-none focus:border-blue-600 bg-white"
                  >
                    <option value="VALIDATED_CREDENTIALS">Validated Credentials - All Checks Passed</option>
                    <option value="SUSPECTED_TAMPERING">Suspected Physical or Digital Tampering</option>
                    <option value="BIOMETRIC_MISMATCH">Biometric Portrait Mismatch</option>
                    <option value="WATCHLIST_HIT">Watchlist / Travel Advisory Hit</option>
                    <option value="IMAGE_DEGRADED">Image Degraded - Secondary Physical Recapture</option>
                    <option value="OTHER">Other Operational Justification</option>
                  </select>
                </div>

                {/* Officer Notes Textarea */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Officer Findings & Justification Notes
                  </label>
                  <textarea
                    rows={4}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Enter detailed inspection notes and secondary verification observations..."
                    className="w-full border border-slate-300 rounded-lg p-3 text-xs text-slate-800 focus:outline-none focus:border-blue-600 resize-none"
                  />
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <div className="text-[11px] text-slate-400">
                    Signing Officer: <strong className="text-slate-700">Inspector Arjun</strong> (ID: BORDER-OFFICER)
                  </div>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-6 py-2.5 rounded-xl font-bold text-xs text-white bg-blue-600 hover:bg-blue-700 shadow-md shadow-blue-500/20 flex items-center gap-2 disabled:opacity-50"
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Signing & Committing to Audit Chain...</span>
                      </>
                    ) : (
                      <span>Commit Decision</span>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
