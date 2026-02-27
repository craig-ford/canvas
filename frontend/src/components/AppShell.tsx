import React from 'react';
import { useAuth } from '../auth/useAuth';
import { Link, useLocation } from 'react-router-dom';
import { QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps): JSX.Element {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navLink = (to: string, label: string) => (
    <Link to={to} className={`text-sm font-medium transition-colors ${location.pathname === to ? 'text-white' : 'text-neutral-400 hover:text-white'}`}>{label}</Link>
  );

  return (
    <div className="min-h-screen bg-neutral-50 font-sans">
      <a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-primary text-white px-4 py-2 rounded">Skip to main content</a>
      <header className="bg-navy text-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex justify-between h-14 items-center">
            <div className="flex items-center gap-5">
              <Link to="/" className="text-lg font-bold tracking-tight hover:text-neutral-200 transition-colors">Canvas</Link>
              {user?.role !== 'gm' && navLink('/dashboard', 'Dashboard')}
              {user?.role === 'admin' && navLink('/admin/users', 'Users')}
            </div>
            <div className="flex items-center gap-4">
              <Link to="/help" title="Help" className="text-[#33A5C4] hover:text-white transition-colors">
                <QuestionMarkCircleIcon className="h-6 w-6 stroke-2" />
              </Link>
              {user && (
                <>
                  <span className="text-sm font-bold text-[#33A5C4]">{user.name}</span>
                  <button onClick={logout} className="text-xs font-bold text-[#33A5C4] hover:text-white transition-colors">Sign out</button>
                </>
              )}
            </div>
          </nav>
        </div>
      </header>
      <main id="main-content">
        {children}
      </main>
    </div>
  );
}
