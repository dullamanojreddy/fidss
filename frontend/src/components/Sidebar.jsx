import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  ShieldCheck,
  LayoutDashboard,
  FileSearch,
  UserCheck,
  AlertTriangle,
  Copy,
  Files,
  FileClock,
  BarChart3,
  Settings,
  LogOut,
  User,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const NAV_ITEMS = [
  { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
  { name: 'Screening Console', path: '/screening-console', icon: FileSearch },
  { name: 'Officer Review', path: '/officer-review', icon: UserCheck },
  { name: 'Watchlist', path: '/watchlist', icon: AlertTriangle },
  { name: 'Duplicate Identity', path: '/duplicate-identity', icon: Copy },
  { name: 'Documents', path: '/documents', icon: Files },
  { name: 'Audit Trail', path: '/audit-trail', icon: FileClock },
  { name: 'Reports', path: '/reports', icon: BarChart3 },
  { name: 'System Settings', path: '/settings', icon: Settings },
];

export const Sidebar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col h-screen select-none shrink-0 sticky top-0">
      {/* Brand Header */}
      <div className="p-5 flex items-center gap-3 border-b border-slate-100">
        <div className="w-10 h-10 rounded-xl bg-blue-600 text-white flex items-center justify-center shadow-md shadow-blue-500/20">
          <ShieldCheck className="w-6 h-6" />
        </div>
        <div>
          <h1 className="font-bold text-slate-900 text-lg leading-tight tracking-tight">FIDSS</h1>
          <p className="text-[11px] text-slate-400 font-medium leading-none mt-1">
            Fake Identity & Document<br />Screening System
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isReview = item.path === '/officer-review';
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-700 font-semibold border-l-4 border-blue-600 pl-2'
                    : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                }`
              }
            >
              <div className="flex items-center gap-3">
                <Icon className="w-4 h-4 shrink-0" />
                <span>{item.name}</span>
              </div>
              {isReview && user?.role === 'SENIOR_OFFICER' && (
                <span className="bg-amber-100 text-amber-800 text-[10px] font-bold px-1.5 py-0.5 rounded-full border border-amber-300">
                  SECONDARY
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Officer Profile Card */}
      <div className="p-3 border-t border-slate-200 bg-slate-50/50 m-3 rounded-xl border space-y-2.5">
        <div className="flex items-center gap-3">
          <div
            className={`w-10 h-10 rounded-full font-bold text-xs flex items-center justify-center shadow-sm shrink-0 ${
              user?.role === 'SENIOR_OFFICER' ? 'bg-amber-600 text-white ring-2 ring-amber-400/40' : 'bg-blue-600 text-white ring-2 ring-blue-400/40'
            }`}
          >
            {user?.role === 'SENIOR_OFFICER' ? 'RV' : 'AR'}
          </div>
          <div className="min-w-0 flex-1">
            <h4 className="text-xs font-bold text-slate-800 truncate">
              {user?.full_name || 'Inspector Arjun'}
            </h4>
            <p className="text-[11px] text-slate-500 truncate">
              {user?.role === 'SENIOR_OFFICER' ? 'Senior Border Officer' : 'Border Officer'}
            </p>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              <span className="text-[10px] text-emerald-600 font-semibold">Active Session</span>
            </div>
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="w-full flex items-center justify-center gap-2 px-3 py-1.5 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100/80 border border-red-200 rounded-lg transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};
