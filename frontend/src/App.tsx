import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import { ShieldCheck, LogOut, User } from 'lucide-react';

// We will create these pages next
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { EnrollPage } from './pages/EnrollPage';
import { VerifyPage } from './pages/VerifyPage';
import { DashboardPage } from './pages/DashboardPage';

const ProtectedRoute = ({ children, requireAdmin = false }: { children: React.ReactNode, requireAdmin?: boolean }) => {
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  
  if (!token) return <Navigate to="/login" replace />;
  if (requireAdmin && user.role !== 'admin') return <Navigate to="/" replace />;
  
  return <>{children}</>;
};

const Navigation = () => {
  const navigate = useNavigate();
  const token = localStorage.getItem('token');
  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!token) return null;

  return (
    <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="text-brand-500 h-8 w-8" />
          <span className="font-bold text-xl tracking-tight text-white">BioLock <span className="text-brand-500">Pro</span></span>
        </div>
        
        <div className="flex items-center gap-6">
          <Link to="/" className="text-slate-300 hover:text-white font-medium transition-colors">Verify</Link>
          <Link to="/enroll" className="text-slate-300 hover:text-white font-medium transition-colors">Enroll</Link>
          {user.role === 'admin' && (
            <Link to="/dashboard" className="text-slate-300 hover:text-brand-400 font-medium transition-colors">Admin Dashboard</Link>
          )}
          
          <div className="flex items-center gap-4 ml-4 pl-4 border-l border-slate-700">
            <div className="flex items-center gap-2 text-slate-400 text-sm">
              <User size={16} />
              <span>{user.username}</span>
            </div>
            <button onClick={handleLogout} className="text-slate-400 hover:text-red-400 transition-colors">
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-brand-500 selection:text-white flex flex-col">
        <Navigation />
        <main className="flex-1 flex flex-col relative">
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/enroll" element={
              <ProtectedRoute>
                <EnrollPage />
              </ProtectedRoute>
            } />
            <Route path="/" element={
              <ProtectedRoute>
                <VerifyPage />
              </ProtectedRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute requireAdmin={true}>
                <DashboardPage />
              </ProtectedRoute>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
