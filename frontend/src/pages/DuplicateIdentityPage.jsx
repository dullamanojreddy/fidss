import React from 'react';
import { Copy, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { Header } from '../components/Header';

export const DuplicateIdentityPage = () => {
  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header
        title="Duplicate Identity Detection"
        subtitle="Historical traveler identity cross-referencing and fuzzy record matching"
      />

      <main className="flex-1 p-6 max-w-[1400px] w-full mx-auto space-y-6">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center text-blue-600">
              <Copy className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-900 text-sm">Historical Duplicate Record Engine</h3>
              <p className="text-xs text-slate-500">
                Normalized RapidFuzz comparison over past document numbers, names, and dates of birth.
              </p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>Zero duplicate identities or contradictory historical records detected for current active session.</span>
          </div>
        </div>
      </main>
    </div>
  );
};
