import { AlertTriangle, CheckCircle2, Microscope, XCircle } from 'lucide-react';

const DETECTORS = [
  ['text_manipulation', 'Text manipulation'], ['copy_move', 'Copy-move'],
  ['compression_analysis', 'Compression / ELA'], ['noise_analysis', 'Noise consistency'],
  ['photo_replacement', 'Photo replacement'], ['stamp_forgery', 'Stamp forgery'],
  ['metadata_analysis', 'Metadata'],
];

const STATUS_STYLES = {
  SUCCESS: ['bg-emerald-50 text-emerald-700 border-emerald-200', CheckCircle2],
  PARTIAL: ['bg-amber-50 text-amber-700 border-amber-200', AlertTriangle],
  INCONCLUSIVE: ['bg-amber-50 text-amber-700 border-amber-200', AlertTriangle],
  FAILED: ['bg-rose-50 text-rose-700 border-rose-200', XCircle],
};

const SEVERITY_STYLES = {
  LOW: 'bg-sky-50 text-sky-700 border-sky-200', MEDIUM: 'bg-amber-50 text-amber-700 border-amber-200',
  HIGH: 'bg-orange-50 text-orange-700 border-orange-200', CRITICAL: 'bg-rose-50 text-rose-700 border-rose-200',
};

function StatusBadge({ status = 'INCONCLUSIVE' }) {
  const [tone, Icon] = STATUS_STYLES[status] || STATUS_STYLES.INCONCLUSIVE;
  return <span className={`inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-bold ${tone}`}><Icon className="h-3 w-3" aria-hidden="true" />{status}</span>;
}

function detectorForEvidence(item) {
  const source = String(item?.source || '');
  return DETECTORS.find(([key]) => source.endsWith(key))?.[0] || null;
}

function formatMetric(value) {
  if (typeof value === 'number') return Number.isInteger(value) ? String(value) : value.toFixed(4);
  if (typeof value === 'boolean') return value ? 'yes' : 'no';
  return String(value);
}

function EvidenceCard({ item }) {
  const region = item.document_region;
  const metrics = item.metrics && typeof item.metrics === 'object' ? Object.entries(item.metrics) : [];
  return (
    <article className="mt-2 rounded-lg border border-slate-200 bg-white p-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="min-w-0"><p className="truncate text-xs font-semibold text-slate-800">{item.category || 'Forensic evidence'}</p><p className="text-[10px] text-slate-400">{item.source || 'Source unavailable'}</p></div>
        <div className="flex items-center gap-1.5"><span className={`rounded-full border px-2 py-0.5 text-[10px] font-bold ${SEVERITY_STYLES[item.severity] || SEVERITY_STYLES.LOW}`}>{item.severity || 'LOW'}</span>{Number.isFinite(item.confidence) && <span className="text-[10px] font-semibold text-slate-500">{(item.confidence * 100).toFixed(1)}%</span>}</div>
      </div>
      {item.description && <p className="mt-2 text-xs leading-relaxed text-slate-600">{item.description}</p>}
      {region && <p className="mt-2 text-[10px] text-slate-500">Region: x {region.x}, y {region.y}, w {region.width}, h {region.height}{region.label ? ` · ${region.label}` : ''}</p>}
      {metrics.length > 0 && <dl className="mt-2 grid grid-cols-1 gap-1 sm:grid-cols-2">{metrics.map(([key, value]) => <div key={key} className="flex justify-between gap-2 rounded bg-slate-50 px-2 py-1 text-[10px]"><dt className="truncate text-slate-400">{key.replaceAll('_', ' ')}</dt><dd className="truncate font-medium text-slate-700">{formatMetric(value)}</dd></div>)}</dl>}
    </article>
  );
}

export default function TamperFindingsPanel({ moduleResult }) {
  if (!moduleResult) return <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm" aria-label="Tampering findings"><h3 className="text-sm font-bold text-slate-800">Tampering &amp; Forensic Findings</h3><p className="mt-3 text-xs text-slate-400">No tampering module result is available.</p></section>;

  const metadata = moduleResult.metadata || {};
  const detectorStatuses = metadata.detector_statuses || {};
  const evidence = Array.isArray(moduleResult.evidence_items) ? moduleResult.evidence_items : [];
  const errors = Array.isArray(moduleResult.errors) ? moduleResult.errors : [];
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm" aria-label="Tampering findings">
      <div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-2"><Microscope className="h-5 w-5 text-blue-600" aria-hidden="true" /><div><h3 className="text-sm font-bold text-slate-800">Tampering &amp; Forensic Findings</h3><p className="text-[10px] text-slate-400">Evidence for review, not a document verdict</p></div></div><StatusBadge status={moduleResult.status} /></div>
      {errors.length > 0 && <div className="mt-3 rounded-lg border border-rose-200 bg-rose-50 p-2 text-xs text-rose-700">{errors.map((error, index) => <p key={`${error}-${index}`}>{error}</p>)}</div>}
      <div className="mt-4 space-y-2">{DETECTORS.map(([key, label]) => {
        const detectorEvidence = evidence.filter((item) => detectorForEvidence(item) === key);
        const status = detectorStatuses[key] || 'INCONCLUSIVE';
        return <div key={key} className="rounded-lg border border-slate-100 bg-slate-50 p-3"><div className="flex items-center justify-between gap-2"><h4 className="text-xs font-semibold text-slate-700">{label}</h4><StatusBadge status={status} /></div>{detectorEvidence.length > 0 ? detectorEvidence.map((item, index) => <EvidenceCard key={item.id || `${key}-${index}`} item={item} />) : <p className="mt-2 text-[11px] text-slate-400">No evidence item produced.</p>}</div>;
      })}</div>
    </section>
  );
}
