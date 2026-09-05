import React, { useState, useRef, useEffect } from 'react';
import { Bell, ChevronDown, User, Shield, Check, AlertOctagon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { screeningApi } from '../api/client';
import { useNavigate } from 'react-router-dom';

export const Header = ({ title, subtitle }) => {
  const { user, profiles, switchProfile, escalatedCount, setEscalatedCount } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);
  const navigate = useNavigate();

  // Load count of escalated cases
  useEffect(() => {
    let isMounted = true;
    const fetchEscalated = async () => {
      try {
        const list = await screeningApi.getEscalated();
        if (isMounted) {
          setEscalatedCount(list?.length || 0);
        }
      } catch (err) {
        // silent fallback
      }
    };
    fetchEscalated();
    const interval = setInterval(fetchEscalated, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, [setEscalatedCount]);

  // Click outside listener
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectProfile = async (username) => {
    setDropdownOpen(false);
    await switchProfile(username);
    if (username === 'senior_verma') {
      navigate('/officer-review');
    }
  };

  const isSenior = user?.role === 'SENIOR_OFFICER';

  return (
    <header className="bg-white border-b border-slate-200 px-8 py-4 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-xl font-bold text-slate-900 tracking-tight">{title}</h1>
        {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-5">
        {/* System Status Pill */}
        <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-full text-xs font-medium text-emerald-800">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>System Status: <strong className="font-semibold text-emerald-700">Operational</strong></span>
        </div>

        {/* Notifications */}
        <div
          onClick={() => isSenior && navigate('/officer-review')}
          className="relative cursor-pointer hover:opacity-80 transition-opacity"
          title={escalatedCount > 0 ? `${escalatedCount} cases awaiting Senior Officer determination` : 'No new notifications'}
        >
          <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-600 border border-slate-200">
            <Bell className="w-4 h-4" />
          </div>
          {escalatedCount > 0 && (
            <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-amber-500 text-white text-[10px] font-bold flex items-center justify-center shadow-sm animate-bounce">
              {escalatedCount}
            </span>
          )}
        </div>

        {/* User Badge with Profile Switcher Dropdown */}
        <div className="relative" ref={dropdownRef}>
          <div
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className={`flex items-center gap-3 pl-3 border-l border-slate-200 cursor-pointer p-1.5 rounded-xl hover:bg-slate-50 transition-colors ${
              dropdownOpen ? 'bg-slate-50 ring-2 ring-blue-500/20' : ''
            }`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs shadow-sm ${
                isSenior ? 'bg-amber-600 text-white ring-2 ring-amber-400/40' : 'bg-blue-600 text-white ring-2 ring-blue-400/40'
              }`}
            >
              {isSenior ? 'RV' : 'AR'}
            </div>
            <div className="hidden sm:block text-left">
              <div className="flex items-center gap-1.5">
                <p className="text-xs font-semibold text-slate-800 leading-none">
                  {user?.full_name || 'Inspector Arjun'}
                </p>
                {isSenior && (
                  <span className="text-[9px] bg-amber-100 text-amber-800 font-bold px-1.5 py-0.2 rounded-full border border-amber-300">
                    SUPERVISOR
                  </span>
                )}
              </div>
              <p className="text-[11px] text-slate-500 leading-none mt-1">
                {isSenior ? 'Senior Border Officer' : 'Border Officer'}
              </p>
            </div>
            <ChevronDown
              className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
                dropdownOpen ? 'rotate-180 text-blue-600' : ''
              }`}
            />
          </div>

          {/* Profile Switcher Dropdown Menu */}
          {dropdownOpen && (
            <div className="absolute right-0 mt-2 w-80 bg-white rounded-2xl shadow-xl border border-slate-200 py-2.5 z-50 animate-in fade-in slide-in-from-top-2 duration-150">
              <div className="px-4 py-2 border-b border-slate-100">
                <p className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                  Switch Officer Profile
                </p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Select identity to test secondary escalation & review
                </p>
              </div>

              <div className="p-2 space-y-1.5">
                {profiles.map((p) => {
                  const isActive = user?.username === p.username;
                  const isVerma = p.username === 'senior_verma';

                  return (
                    <button
                      key={p.username}
                      onClick={() => handleSelectProfile(p.username)}
                      className={`w-full text-left p-3 rounded-xl transition-all flex items-start justify-between border ${
                        isActive
                          ? isVerma
                            ? 'bg-amber-50/70 border-amber-300 text-amber-950 shadow-sm'
                            : 'bg-blue-50/70 border-blue-300 text-blue-950 shadow-sm'
                          : 'bg-white border-transparent hover:bg-slate-50 hover:border-slate-200 text-slate-700'
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <div
                          className={`w-9 h-9 rounded-xl flex items-center justify-center font-bold text-xs shadow-sm mt-0.5 shrink-0 ${
                            isVerma ? 'bg-amber-600 text-white' : 'bg-blue-600 text-white'
                          }`}
                        >
                          {p.initials}
                        </div>
                        <div className="min-w-0">
                          <div className="flex items-center gap-1.5">
                            <h4 className="text-xs font-bold text-slate-900 truncate">
                              {p.full_name}
                            </h4>
                            {isVerma && (
                              <span className="text-[9px] bg-amber-100 text-amber-800 font-bold px-1.5 py-0.5 rounded border border-amber-300 shrink-0">
                                SENIOR
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-500 mt-0.5">
                            {p.title}
                          </p>

                          {isVerma && escalatedCount > 0 && (
                            <div className="mt-1.5 inline-flex items-center gap-1 bg-rose-50 text-rose-700 text-[10px] font-bold px-2 py-0.5 rounded-full border border-rose-200">
                              <AlertOctagon className="w-3 h-3 text-rose-600" />
                              <span>{escalatedCount} Escalated Case{escalatedCount > 1 ? 's' : ''} Awaiting Review</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {isActive ? (
                        <span className="w-5 h-5 rounded-full bg-emerald-500 text-white flex items-center justify-center shrink-0 mt-1">
                          <Check className="w-3 h-3 stroke-[3]" />
                        </span>
                      ) : (
                        <span className="text-[10px] font-semibold text-slate-400 hover:text-slate-600 bg-slate-100 px-2 py-1 rounded-md shrink-0 mt-1">
                          Switch
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>

              <div className="px-3 py-2 border-t border-slate-100 bg-slate-50/60 rounded-b-xl text-[11px] text-slate-500 flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-slate-400" />
                <span>Secondary Escalations route directly to Senior Officer</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
