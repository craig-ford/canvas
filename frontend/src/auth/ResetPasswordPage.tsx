import { useState, FormEvent } from 'react';
import { useAuth } from './useAuth';
import { apiClient as api } from '../api/client';

export function ResetPasswordPage({ onBack }: { onBack?: () => void }) {
  const { user, refreshToken } = useAuth();
  const forced = user?.must_reset_password;
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    if (newPassword.length < 8) { setError('New password must be at least 8 characters'); return; }
    if (newPassword !== confirm) { setError('Passwords do not match'); return; }
    setLoading(true);
    try {
      await api.post('/auth/reset-password', {
        ...(forced ? {} : { current_password: currentPassword }),
        new_password: newPassword,
      });
      await refreshToken();
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to reset password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-ice font-sans">
      <div className="bg-white p-10 rounded-xl shadow-lg w-full max-w-sm border border-neutral-100">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-navy tracking-tight">Set New Password</h1>
          <p className="text-sm text-neutral-500 mt-1">
            {forced ? `Hi ${user?.name}, please choose a new password to continue.` : 'Enter your current password and choose a new one.'}
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-warning-pale border border-warning-dark/30 text-neutral-800 text-sm rounded-lg px-4 py-2.5 text-center">{error}</div>
          )}
          {!forced && (
            <div>
              <label className="block text-sm font-medium text-neutral-800 mb-1">Current Password</label>
              <input type="password" value={currentPassword} onChange={e => setCurrentPassword(e.target.value)} required
                className="w-full border border-neutral-100 rounded-lg px-3.5 py-2.5 text-sm text-neutral-900 bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary" />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-neutral-800 mb-1">New Password</label>
            <input type="password" value={newPassword} onChange={e => setNewPassword(e.target.value)} required autoFocus
              className="w-full border border-neutral-100 rounded-lg px-3.5 py-2.5 text-sm text-neutral-900 bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary" />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-800 mb-1">Confirm New Password</label>
            <input type="password" value={confirm} onChange={e => setConfirm(e.target.value)} required
              className="w-full border border-neutral-100 rounded-lg px-3.5 py-2.5 text-sm text-neutral-900 bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary" />
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-primary text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 transition-colors">
            {loading ? 'Updating…' : 'Set Password'}
          </button>
        </form>
        {!forced && onBack && (
          <button onClick={onBack} className="w-full mt-3 text-sm text-primary hover:underline">← Back to sign in</button>
        )}
      </div>
    </div>
  );
}
