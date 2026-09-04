import { AlertTriangle, CheckCircle2, ScanFace, UserX } from 'lucide-react';

const styles = {
  MATCH: ['bg-emerald-50 text-emerald-700 border-emerald-200', CheckCircle2],
  MISMATCH: ['bg-rose-50 text-rose-700 border-rose-200', UserX],
  INCONCLUSIVE: ['bg-amber-50 text-amber-700 border-amber-200', AlertTriangle],
  NO_FACE: ['bg-amber-50 text-amber-700 border-amber-200', AlertTriangle],
  MULTIPLE_FACES: ['bg-amber-50 text-amber-700 border-amber-200', AlertTriangle],
};

export default function FaceMatchCard({ moduleResult }) {
  const metadata = moduleResult?.metadata || {};
  const outcome = metadata.outcome || (moduleResult?.status === 'SUCCESS' ? 'MATCH' : 'INCONCLUSIVE');
  const [tone, Icon] = styles[outcome] || styles.INCONCLUSIVE;
  const similarity = Number.isFinite(metadata.similarity_percent)
    ? metadata.similarity_percent
    : Number.isFinite(metadata.similarity) ? Math.max(0, metadata.similarity * 100) : null;
  const message = moduleResult?.errors?.[0] || (outcome === 'MATCH' ? 'Selfie matches the document portrait.' : outcome === 'MISMATCH' ? 'Selfie is below the configured match threshold.' : 'A reliable face comparison was not available.');

  return (
    <section className="bg-white rounded-xl border border-slate-200 shadow-sm p-4" aria-label="Face verification result">
      <div className="flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ScanFace className="w-5 h-5 text-blue-600" aria-hidden="true" />
          <h3 className="font-bold text-slate-800 text-sm">Face Verification</h3>
        </div>
        <span className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[10px] font-bold ${tone}`}>
          <Icon className="w-3.5 h-3.5" aria-hidden="true" />{outcome.replaceAll('_', ' ')}
        </span>
      </div>
      {similarity !== null && (
        <div className="mt-4">
          <div className="flex justify-between text-xs mb-1.5"><span className="text-slate-500">Cosine similarity</span><span className="font-bold text-slate-800">{similarity.toFixed(1)}%</span></div>
          <div className="h-2 rounded-full bg-slate-100 overflow-hidden"><div className={`h-full ${outcome === 'MATCH' ? 'bg-emerald-500' : 'bg-rose-500'}`} style={{ width: `${Math.min(100, similarity)}%` }} /></div>
        </div>
      )}
      <p className="mt-3 text-xs leading-relaxed text-slate-500">{message}</p>
      <div className="mt-3 grid grid-cols-2 gap-2 text-[11px]">
        <div className="rounded-lg bg-slate-50 p-2"><span className="text-slate-400">Document faces</span><p className="font-semibold text-slate-700">{metadata.document_face_count ?? '—'}</p></div>
        <div className="rounded-lg bg-slate-50 p-2"><span className="text-slate-400">Selfie faces</span><p className="font-semibold text-slate-700">{metadata.selfie_face_count ?? '—'}</p></div>
      </div>
    </section>
  );
}
