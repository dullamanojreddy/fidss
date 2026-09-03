import React, { useState, useEffect } from 'react';
import { Settings, Sliders, Cpu, Save, Loader2, Check } from 'lucide-react';
import { Header } from '../components/Header';
import { settingsApi } from '../api/client';
import { useAuth } from '../context/AuthContext';

export const SystemSettingsPage = () => {
  const { user } = useAuth();
  const [settings, setSettings] = useState({});
  const [models, setModels] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState('');

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    setLoading(true);
    try {
      const [setData, modelData] = await Promise.all([
        settingsApi.get(),
        settingsApi.getModels(),
      ]);
      setSettings(setData.settings || {});
      setModels(modelData || []);
    } catch (err) {
      console.error('Error fetching settings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await settingsApi.update(settings);
      setSavedMsg('Settings updated and audited successfully.');
      setTimeout(() => setSavedMsg(''), 4000);
    } catch (err) {
      console.error('Error saving settings:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col bg-slate-50 min-h-screen">
      <Header
        title="System Settings & Model Registry"
        subtitle="Admin-controlled thresholds, weights, and analytical model runtime registry"
      />

      <main className="flex-1 p-6 max-w-[1400px] w-full mx-auto space-y-6">
        {savedMsg && (
          <div className="p-4 bg-emerald-50 text-emerald-800 rounded-xl border border-emerald-200 text-xs font-semibold flex items-center gap-2">
            <Check className="w-4 h-4 text-emerald-600" />
            <span>{savedMsg}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Policy & Thresholds Form */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5">
            <div className="flex items-center gap-3 border-b border-slate-100 pb-3">
              <Sliders className="w-5 h-5 text-blue-600" />
              <h3 className="font-bold text-slate-900 text-sm">Screening & Verification Thresholds</h3>
            </div>

            <form onSubmit={handleSave} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Face Similarity Match Threshold (Cosine)
                </label>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="0.5"
                    max="0.9"
                    step="0.01"
                    value={settings.face_similarity_threshold ?? 0.65}
                    onChange={(e) => setSettings({ ...settings, face_similarity_threshold: parseFloat(e.target.value) })}
                    className="flex-1"
                  />
                  <span className="font-bold text-slate-800 w-12 text-right">
                    {settings.face_similarity_threshold ?? 0.65}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Recommended baseline: 0.65 for ArcFace ResNet50.</p>
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">
                  Minimum Quality Sharpness (Laplacian Variance)
                </label>
                <input
                  type="number"
                  value={settings.quality_min_sharpness ?? 85.0}
                  onChange={(e) => setSettings({ ...settings, quality_min_sharpness: parseFloat(e.target.value) })}
                  className="w-full border border-slate-300 rounded-lg p-2 text-xs"
                />
              </div>

              <div>
                <label className="block font-semibold text-slate-700 mb-1">Forensic Tampering Sensitivity</label>
                <select
                  value={settings.tamper_sensitivity ?? 'STANDARD'}
                  onChange={(e) => setSettings({ ...settings, tamper_sensitivity: e.target.value })}
                  className="w-full border border-slate-300 rounded-lg p-2 text-xs"
                >
                  <option value="LOW">Low (High tolerance for compression noise)</option>
                  <option value="STANDARD">Standard (Balanced checkpoint preset)</option>
                  <option value="HIGH">High (Flag subtle pixel anomalies)</option>
                </select>
              </div>

              <div className="pt-3 border-t border-slate-100 flex justify-end">
                <button
                  type="submit"
                  disabled={saving}
                  className="px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-sm flex items-center gap-2 disabled:opacity-50"
                >
                  {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                  <span>Save Configuration</span>
                </button>
              </div>
            </form>
          </div>

          {/* Model Registry List */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center gap-3 border-b border-slate-100 pb-3">
              <Cpu className="w-5 h-5 text-purple-600" />
              <h3 className="font-bold text-slate-900 text-sm">Registered AI/CV Model Artifacts</h3>
            </div>

            <div className="space-y-3">
              {models.map((m) => (
                <div key={m.id} className="p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs">
                  <div className="flex items-center justify-between font-semibold text-slate-800">
                    <span>{m.model_name}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 font-bold">
                      Active
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] text-slate-500">
                    <div>Version: <strong className="text-slate-700">{m.version}</strong></div>
                    <div>Runtime: <strong className="text-slate-700">{m.runtime}</strong></div>
                  </div>
                  <div className="mt-1 text-[10px] text-slate-400 font-mono truncate">
                    Checksum: {m.checksum}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};
