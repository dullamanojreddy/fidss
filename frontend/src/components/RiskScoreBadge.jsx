const tones = {
  CLEAR: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  REVIEW_RECOMMENDED: 'bg-amber-50 text-amber-700 border-amber-200',
  ENHANCED_REVIEW_RECOMMENDED: 'bg-orange-50 text-orange-700 border-orange-200',
  INCONCLUSIVE: 'bg-rose-50 text-rose-700 border-rose-200',
};

export default function RiskScoreBadge({ score = 0, level = 'INCONCLUSIVE', showScore = true, className = '' }) {
  const safeScore = Number.isFinite(Number(score)) ? Math.min(100, Math.max(0, Number(score))) : 0;
  return (
    <span className={`inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-[10px] font-bold ${tones[level] || tones.INCONCLUSIVE} ${className}`} title={`Risk score ${safeScore.toFixed(1)} out of 100`}>
      <span className="h-1.5 w-1.5 rounded-full bg-current" aria-hidden="true" />
      {level.replaceAll('_', ' ')}{showScore ? ` · ${safeScore.toFixed(1)}/100` : ''}
    </span>
  );
}
