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
  AlertTriangle,
  ArrowRight,
  ShieldAlert,
  User,
} from 'lucide-react';
import { Header } from '../components/Header';
import { screeningApi } from '../api/client';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const PRIMARY_DECISIONS = [
  { id: 'ACCEPT', label: 'Accept & Clear', icon: CheckCircle2, color: 'bg-emerald-600 hover:bg-emerald-700 text-white', border: 'border-emerald-600' },
  { id: 'REJECT', label: 'Reject Entry', icon: XCircle, color: 'bg-rose-600 hover:bg-rose-700 text-white', border: 'border-rose-600' },
  { id: 'ESCALATE', label: 'Escalate to Secondary', icon: AlertOctagon, color: 'bg-amber-600 hover:bg-amber-700 text-white', border: 'border-amber-600' },
  { id: 'REQUEST_RECAPTURE', label: 'Request Recapture', icon: RefreshCw, color: 'bg-blue-600 hover:bg-blue-700 text-white', border: 'border-blue-600' },
  { id: 'MARK_INCONCLUSIVE', label: 'Mark Inconclusive', icon: HelpCircle, color: 'bg-slate-600 hover:bg-slate-700 text-white', border: 'border-slate-600' },
];

const SENIOR_DECISIONS = [
  { id: 'ACCEPT', label: 'Approve & Clear Entry (Senior Override)', icon: CheckCircle2, color: 'bg-emerald-600 hover:bg-emerald-700 text-white', border: 'border-emerald-600' },
  { id: 'REJECT', label: 'Refuse Entry & Issue Detention Order', icon: XCircle, color: 'bg-rose-600 hover:bg-rose-700 text-white', border: 'border-rose-600' },
  { id: 'REQUEST_RECAPTURE', label: 'Order Secondary Physical Interview', icon: RefreshCw, color: 'bg-blue-600 hover:bg-blue-700 text-white', border: 'border-blue-600' },
  { id: 'MARK_INCONCLUSIVE', label: 'Hold for Investigation', icon: HelpCircle, color: 'bg-slate-600 hover:bg-slate-700 text-white', border: 'border-slate-600' },
];

export const OfficerReviewPage = () => {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user, isSeniorOfficer, setEscalatedCount } = useAuth();

  const [screening, setScreening] = useState(null);
  const [evidenceList, setEvidenceList] = useState([]);
  const [escalatedCases, setEscalatedCases] = useState([]);
  const [selectedEscalatedId, setSelectedEscalatedId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [selectedDecision, setSelectedDecision] = useState('ACCEPT');
  const [reason, setReason] = useState('VALIDATED_CREDENTIALS');
  const [notes, setNotes] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [escalatedDetails, setEscalatedDetails] = useState(null);

  useEffect(() => {
    loadReviewData();
  }, [id, isSeniorOfficer]);

  const loadReviewData = async () => {
    setLoading(true);
    try {
      // 1. Fetch escalated list
      let escalatedList = [];
      try {
        escalatedList = await screeningApi.getEscalated();
        setEscalatedCases(escalatedList || []);
        setEscalatedCount(escalatedList?.length || 0);
      } catch (e) {
        console.warn('Could not fetch escalated list:', e);
      }

      let targetId = id;

      // If Senior Officer is logged in and no specific ID is given, open the first escalated case
      if (isSeniorOfficer && !targetId && escalatedList && escalatedList.length > 0) {
        targetId = escalatedList[0].screening_id;
        setSelectedEscalatedId(targetId);
      } else if (!targetId) {
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
      setSelectedEscalatedId(targetId);

      const ev = await screeningApi.getEvidence(data.id);
      setEvidenceList(ev || []);

      // Check if this case has an escalation record
      const matchEscalated = escalatedList.find((e) => e.screening_id === data.id);
      setEscalatedDetails(matchEscalated || null);

      // Check if existing review
      const existing = await screeningApi.getReview(data.id);
      if (existing) {
        setSelectedDecision(existing.decision);
        setReason(existing.reason);
        setNotes(existing.notes || '');
      } else {
        setSelectedDecision(isSeniorOfficer ? 'ACCEPT' : 'ESCALATE');
      }
    } catch (err) {
      console.error('Error fetching review data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectCase = async (caseId) => {
    setSelectedEscalatedId(caseId);
    setLoading(true);
    try {
      const data = await screeningApi.getById(caseId);
      setScreening(data);
      const ev = await screeningApi.getEvidence(data.id);
      setEvidenceList(ev || []);

      const matchEscalated = escalatedCases.find((e) => e.screening_id === data.id);
      setEscalatedDetails(matchEscalated || null);

      const existing = await screeningApi.getReview(data.id);
      if (existing) {
        setSelectedDecision(existing.decision);
        setReason(existing.reason);
        setNotes(existing.notes || '');
      }
    } catch (err) {
      console.error('Error switching case:', err);
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

      // Refresh escalated cases count
      const updatedEscalated = await screeningApi.getEscalated();
      setEscalatedCases(updatedEscalated || []);
      setEscalatedCount(updatedEscalated?.length || 0);

      if (selectedDecision === 'ESCALATE') {
        setSuccessMessage(
          `Case Ref ${screening?.screening_number} has been escalated to Senior Officer (Superintendent Rajesh Verma). Switch profiles via the header arrow to review and finalize.`
        );
      } else {
        setSuccessMessage(
          `Operational determination recorded by ${user?.full_name || 'Officer'} and cryptographically logged to audit trail.`
        );
      }
      setTimeout(() => setSuccessMessage(''), 6000);
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

  const activeDecisions = isSeniorOfficer ? SENIOR_DECISIONS : PRIMARY_DECISIONS;
  const travelerName =
    screening?.extracted_fields?.['name'] ||
    screening?.extracted_fields?.['Full Name'] ||
    `${screening?.extracted_fields?.['Given Name'] || ''} ${screening?.extracted_fields?.['Surname'] || ''}`.trim() ||
    'Traveler (Identity Under Verification)';

  const passportNumber =
    screening?.extracted_fields?.['document_number'] ||
    screening?.extracted_fields?.['Passport Number'] ||
    screening?.extracted_fields?.['Document Number'] ||
    'N/A';

  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header
        title={isSeniorOfficer ? "Senior Supervisor Review" : "Officer Review"}
        subtitle={
          isSeniorOfficer
            ? "Secondary escalation queue & supervisor determination"
            : "Human-in-the-loop operational decision recording"
        }
      />

      <main className="flex-1 p-6 max-w-[1400px] w-full mx-auto space-y-5">
        {/* Top Navigation Bar */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => navigate('/screening-console')}
            className="flex items-center gap-2 text-xs font-semibold text-slate-600 hover:text-slate-900 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Console</span>
          </button>
          <span className="text-xs text-slate-400 font-medium">
            Screening Ref: <strong className="text-slate-700">{screening?.screening_number}</strong>
          </span>
        </div>

        {/* Secondary Escalation Queue Banner for Senior Officer */}
        {isSeniorOfficer && (
          <div className="bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-transparent border border-amber-300/80 rounded-2xl p-4 shadow-sm">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-amber-600 text-white flex items-center justify-center font-bold shadow-sm">
                  <ShieldAlert className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-amber-950">
                    Secondary Inspection Queue — Senior Officer Determination
                  </h3>
                  <p className="text-xs text-amber-800/80">
                    {escalatedCases.length > 0
                      ? `${escalatedCases.length} case(s) escalated by Primary Border Officers awaiting supervisor clearance.`
                      : 'No pending escalations. All secondary reviews are up to date.'}
                  </p>
                </div>
              </div>

              {escalatedCases.length > 0 && (
                <span className="bg-amber-600 text-white text-xs font-bold px-2.5 py-1 rounded-full shadow-sm">
                  {escalatedCases.length} Pending
                </span>
              )}
            </div>

            {/* Escalated Cases Selector Pill Tabs */}
            {escalatedCases.length > 0 && (
              <div className="flex items-center gap-2 overflow-x-auto pt-1 pb-0.5">
                {escalatedCases.map((c) => {
                  const isSelected = selectedEscalatedId === c.screening_id;
                  return (
                    <button
                      key={c.screening_id}
                      onClick={() => handleSelectCase(c.screening_id)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold border transition-all shrink-0 ${
                        isSelected
                          ? 'bg-amber-600 text-white border-amber-700 shadow-sm'
                          : 'bg-white text-slate-700 border-slate-200 hover:bg-amber-50/50 hover:border-amber-300'
                      }`}
                    >
                      <User className="w-3.5 h-3.5" />
                      <div className="text-left">
                        <div className="font-bold leading-tight">{c.traveler_name}</div>
                        <div className="text-[10px] opacity-80">{c.screening_number} • No: {c.document_number}</div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Success / Escalation Feedback Alert */}
        {successMessage && (
          <div className="p-4 bg-emerald-50 text-emerald-900 rounded-xl border border-emerald-300 text-xs font-semibold flex items-start gap-3 shadow-sm animate-in fade-in">
            <Check className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            <div>
              <p className="font-bold text-emerald-950">Action Recorded Successfully</p>
              <p className="mt-0.5 text-emerald-800">{successMessage}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: Evidence Summary & Document Reference (5 cols) */}
          <div className="lg:col-span-5 space-y-5">
            {/* Escalation Notes Box (if escalated) */}
            {escalatedDetails && (
              <div className="bg-amber-50/80 border border-amber-300 rounded-xl p-4 shadow-sm">
                <div className="flex items-center gap-2 text-xs font-bold text-amber-900 mb-1.5">
                  <AlertOctagon className="w-4 h-4 text-amber-700" />
                  <span>Primary Officer Escalation Dossier</span>
                </div>
                <div className="text-xs text-amber-950 space-y-1">
                  <p>
                    <strong>Escalated by:</strong> {escalatedDetails.escalated_by}
                  </p>
                  <p>
                    <strong>Reason:</strong> {escalatedDetails.escalation_reason}
                  </p>
                  {escalatedDetails.escalation_notes && (
                    <p className="bg-white/80 p-2 rounded-lg border border-amber-200 mt-1 italic text-slate-700">
                      "{escalatedDetails.escalation_notes}"
                    </p>
                  )}
                </div>
              </div>
            )}

            {/* Document Preview Card */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-3">Document & Biometric Summary</h3>
              <div className="bg-slate-100 rounded-lg overflow-hidden border border-slate-200 p-2 flex items-center justify-center mb-4">
                <img
                  src={screening?.document_preview_url || '/static/uploads/demo_passport.png'}
                  alt="Document"
                  className="max-h-48 object-contain rounded shadow-sm"
                />
              </div>

              <div className="space-y-2 text-xs">
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-400">Automated Recommendation</span>
                  <span className="font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded-full border border-slate-200">
                    {screening?.screening_level}
                  </span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-400">Calculated Risk Score</span>
                  <span className="font-bold text-slate-800">{screening?.overall_risk_score} / 100</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-400">Traveler Name</span>
                  <span className="font-bold text-slate-900">{travelerName}</span>
                </div>
                <div className="flex justify-between py-1 border-b border-slate-100">
                  <span className="text-slate-400">Document Number</span>
                  <span className="font-bold text-slate-900">{passportNumber}</span>
                </div>
                {screening?.extracted_fields?.['date_of_birth'] && (
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-400">Date of Birth</span>
                    <span className="font-medium text-slate-800">{screening.extracted_fields['date_of_birth']}</span>
                  </div>
                )}
                {screening?.extracted_fields?.['date_of_expiry'] && (
                  <div className="flex justify-between py-1">
                    <span className="text-slate-400">Date of Expiry</span>
                    <span className="font-medium text-slate-800">{screening.extracted_fields['date_of_expiry']}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Granular Evidence Items */}
            <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm">
              <h3 className="text-sm font-bold text-slate-900 mb-3">
                Supporting Evidence Findings ({evidenceList.length})
              </h3>
              <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
                {evidenceList.map((ev) => (
                  <div key={ev.id} className="p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-slate-800">{ev.category}</span>
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded font-bold ${
                          ev.severity === 'CRITICAL'
                            ? 'bg-rose-100 text-rose-800 border border-rose-300'
                            : ev.severity === 'HIGH'
                            ? 'bg-amber-100 text-amber-800 border border-amber-300'
                            : 'bg-blue-50 text-blue-700'
                        }`}
                      >
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
              <div className="flex items-center justify-between mb-1">
                <h3 className="text-base font-bold text-slate-900">
                  {isSeniorOfficer ? 'Supervisor Operational Determination' : 'Record Operational Decision'}
                </h3>
                <span
                  className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                    isSeniorOfficer
                      ? 'bg-amber-100 text-amber-900 border-amber-300'
                      : 'bg-blue-100 text-blue-900 border-blue-300'
                  }`}
                >
                  {isSeniorOfficer ? 'SECONDARY SUPERVISOR' : 'PRIMARY OFFICER'}
                </span>
              </div>
              <p className="text-xs text-slate-500 mb-5">
                {isSeniorOfficer
                  ? 'As Senior Border Officer, your determination overrides primary screening and renders the final entry clearance.'
                  : 'The automated system provides decision support. The authorized border officer renders the legal determination.'}
              </p>

              <form onSubmit={handleSubmit} className="space-y-5">
                {/* Decision Selector Buttons */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-2">
                    {isSeniorOfficer ? 'Senior Determination Decision' : 'Operational Decision'}
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {activeDecisions.map((d) => {
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
                    <option value="SUPERVISOR_OVERRIDE_CLEARED">Supervisor Override - Identity Verified Legitimate</option>
                    <option value="SUSPECTED_TAMPERING">Suspected Physical or Digital Tampering</option>
                    <option value="BIOMETRIC_MISMATCH">Biometric Portrait Mismatch</option>
                    <option value="WATCHLIST_HIT">Watchlist / Travel Advisory Hit</option>
                    <option value="SECONDARY_PHYSICAL_INTERVIEW">Secondary Physical Interview Required</option>
                    <option value="OTHER">Other Operational Justification</option>
                  </select>
                </div>

                {/* Officer Notes Textarea */}
                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    {isSeniorOfficer ? 'Senior Determination Notes & Findings' : 'Officer Findings & Justification Notes'}
                  </label>
                  <textarea
                    rows={4}
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder={
                      isSeniorOfficer
                        ? 'Enter senior supervisor inspection notes, interview findings, and final legal authorization notes...'
                        : 'Enter detailed inspection notes and reason for escalating to secondary supervisor...'
                    }
                    className="w-full border border-slate-300 rounded-lg p-3 text-xs text-slate-800 focus:outline-none focus:border-blue-600 resize-none"
                  />
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  <div className="text-[11px] text-slate-500">
                    Signing Officer:{' '}
                    <strong className="text-slate-800 font-bold">
                      {user?.full_name || 'Inspector Arjun'}
                    </strong>{' '}
                    <span className="text-slate-400">
                      ({user?.role === 'SENIOR_OFFICER' ? 'SENIOR-SUPERVISOR' : 'BORDER-OFFICER'})
                    </span>
                  </div>
                  <button
                    type="submit"
                    disabled={submitting}
                    className={`px-6 py-2.5 rounded-xl font-bold text-xs text-white shadow-md flex items-center gap-2 disabled:opacity-50 transition-all ${
                      isSeniorOfficer
                        ? 'bg-amber-600 hover:bg-amber-700 shadow-amber-500/20'
                        : 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/20'
                    }`}
                  >
                    {submitting ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Signing & Committing to Audit Chain...</span>
                      </>
                    ) : (
                      <span>{isSeniorOfficer ? 'Commit Senior Determination' : 'Commit Decision'}</span>
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
