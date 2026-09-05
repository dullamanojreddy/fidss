import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '../api/client';

const AuthContext = createContext(null);

export const PROFILES = [
  {
    username: 'arjun',
    full_name: 'Inspector Arjun',
    role: 'OFFICER',
    title: 'Border Officer (Primary Inspection)',
    badge: 'PRIMARY',
    initials: 'AR',
    color: 'bg-blue-600 text-white',
    password: 'OfficerArjun2026!',
  },
  {
    username: 'senior_verma',
    full_name: 'Superintendent Rajesh Verma',
    role: 'SENIOR_OFFICER',
    title: 'Senior Border Officer (Secondary Supervisor)',
    badge: 'SECONDARY SUPERVISOR',
    initials: 'RV',
    color: 'bg-amber-600 text-white',
    password: 'SeniorVerma2026!',
  },
];

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('fidss_user');
    return saved ? JSON.parse(saved) : PROFILES[0];
  });
  const [loading, setLoading] = useState(false);
  const [escalatedCount, setEscalatedCount] = useState(0);

  const login = async (username, password) => {
    setLoading(true);
    try {
      const data = await authApi.login(username, password);
      localStorage.setItem('fidss_token', data.access_token);
      localStorage.setItem('fidss_user', JSON.stringify(data.user));
      setUser(data.user);
      return data;
    } finally {
      setLoading(false);
    }
  };

  const switchProfile = async (targetUsername) => {
    const target = PROFILES.find((p) => p.username === targetUsername);
    if (!target) return;
    setLoading(true);
    try {
      await login(target.username, target.password);
    } catch (err) {
      console.warn('Backend login switch failed, setting client profile directly:', err);
      localStorage.setItem('fidss_user', JSON.stringify(target));
      setUser(target);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('fidss_token');
    localStorage.removeItem('fidss_user');
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profiles: PROFILES,
        switchProfile,
        isSeniorOfficer: user?.role === 'SENIOR_OFFICER',
        login,
        logout,
        loading,
        escalatedCount,
        setEscalatedCount,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
