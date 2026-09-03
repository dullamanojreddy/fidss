import React, { useState, useEffect } from 'react';
import {
  FileClock,
  ShieldCheck,
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Hash,
  Clock,
  User,
  Zap,
  Loader2,
} from 'lucide-react';
import { Header } from '../components/Header';
import { auditApi } from '../api/client';

export const AuditTrailPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [tampering, setTampering] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    setLoading(true);
    try {
      const data = await auditApi.getLogs(50);
      setLogs(data);
    } catch (err) {
      console.error('Error fetching audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleVerify = async () => {
    setVerifying(true);
    try {
      const res = await auditApi.verifyChain('SID-2026-05-21-00124');
      setVerificationResult(res);
    } catch (err) {
      console.error('Verification error:', err);
    } finally {
      setVerifying(false);
    }
  };

  const handleSimulateTampering = async () => {
    setTampering(true);
    try {
      await auditApi.tamperDemo('SID-2026-05-21-00124');
      await loadAuditLogs();
      // Re-verify immediately to show detection
      const res = await auditApi.verifyChain('SID-2026-05-21-00124');
      setVerificationResult(res);
    } catch (err) {
      console.error('Tamper demo error:', err);
    } finally {
      setTampering(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header
        title="Cryptographic Audit Trail"
        subtitle="Tamper-evident SHA-256 hash chain and independently verifiable investigation history"
      />

      <main className="flex-1 p-6 max-w-[1500px] w-full mx-auto space-y-6">
        {/* Verification Status Banner */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
              <Hash className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Audit Chain Verification Engine</h3>
              <p className="text-xs text-slate-500 mt-0.5">
                Each event links cryptographically to the prior event via SHA-256(previous_hash + canonical_event + timestamp).
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleVerify}
              disabled={verifying}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-sm disabled:opacity-50"
            >
              {verifying ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShieldCheck className="w-4 h-4" />}
              <span>Verify Audit Integrity</span>
            </button>

            <button
              onClick={handleSimulateTampering}
              disabled={tampering}
              className="flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold text-rose-700 bg-rose-50 hover:bg-rose-100 border border-rose-200 disabled:opacity-50"
              title="Deliberately tamper with database row to demonstrate hackathon proof of detection"
            >
              {tampering ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              <span>Simulate Row Tampering (Demo)</span>
            </button>
          </div>
        </div>

        {/* Verification Result Alert */}
        {verificationResult && (
          <div
            className={`p-4 rounded-xl border flex items-start gap-3 text-xs ${
              verificationResult.chain_valid
                ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                : 'bg-rose-50 border-rose-300 text-rose-900'
            }`}
          >
            {verificationResult.chain_valid ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0 mt-0.5" />
            ) : (
              <ShieldAlert className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="flex items-center gap-2">
                <strong className="font-bold text-sm">
                  {verificationResult.status === 'VERIFIED'
                    ? 'AUDIT CHAIN INTEGRITY: VERIFIED'
                    : 'AUDIT INTEGRITY FAILURE DETECTED'}
                </strong>
                <span className="text-[11px] px-2 py-0.5 rounded-full font-bold bg-white/80 border">
                  Checked {verificationResult.total_events} Blocks
                </span>
              </div>
              <p className="mt-1 leading-relaxed">{verificationResult.message}</p>
            </div>
          </div>
        )}

        {/* Hash Chain Timeline Cards */}
        <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-slate-900 text-sm">Chronological Cryptographic Blocks</h3>
            <button
              onClick={loadAuditLogs}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-800"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh</span>
            </button>
          </div>

          {loading ? (
            <div className="p-8 flex justify-center">
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            </div>
          ) : logs.length === 0 ? (
            <p className="text-xs text-slate-400 py-6 text-center">No audit records recorded yet.</p>
          ) : (
            <div className="space-y-3">
              {logs.map((log) => (
                <div
                  key={log.id}
                  className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 hover:bg-slate-50 hover:border-slate-300 transition-colors text-xs font-mono"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2 mb-2 font-sans">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded font-bold bg-blue-100 text-blue-800 text-[11px]">
                        Block #{log.block_index ?? 0}
                      </span>
                      <span className="font-bold text-slate-800">{log.event_type}</span>
                    </div>
                    <div className="flex items-center gap-4 text-[11px] text-slate-500 font-sans">
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {new Date(log.timestamp).toLocaleString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <User className="w-3.5 h-3.5" />
                        Actor: {log.actor_id}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px] mt-2">
                    <div className="p-2 rounded bg-white border border-slate-200">
                      <span className="text-slate-400 font-sans text-[10px] block">PREVIOUS HASH</span>
                      <span className="text-slate-600 truncate block">
                        {log.previous_hash || 'GENESIS_ROOT (Block 0)'}
                      </span>
                    </div>
                    <div className="p-2 rounded bg-white border border-slate-200">
                      <span className="text-slate-400 font-sans text-[10px] block">CURRENT SHA-256 HASH</span>
                      <span className="text-blue-700 font-semibold truncate block">{log.current_hash}</span>
                    </div>
                  </div>

                  <div className="mt-2 p-2 rounded bg-white border border-slate-200 overflow-x-auto text-[11px] text-slate-700">
                    <span className="text-slate-400 font-sans text-[10px] block mb-1">CANONICAL PAYLOAD</span>
                    <pre className="text-[11px] whitespace-pre-wrap">{log.event_payload_json}</pre>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
};
