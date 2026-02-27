import { useState, useEffect } from 'react';
import { apiClient as api } from '../api/client';

interface UserRow { id: string; name: string; email: string; role: string; is_active: boolean; must_reset_password: boolean; }

export function UsersPage() {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [resetUser, setResetUser] = useState<UserRow | null>(null);
  const [tempPassword, setTempPassword] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => { api.get('/auth/users').then(r => setUsers(r.data.data)); }, []);

  const doReset = async () => {
    if (!resetUser) return;
    setLoading(true);
    try {
      const r = await api.post(`/auth/users/${resetUser.id}/reset-password`);
      setTempPassword(r.data.data.temporary_password);
      setUsers(prev => prev.map(u => u.id === resetUser.id ? { ...u, must_reset_password: true } : u));
    } catch { /* */ } finally { setLoading(false); }
  };

  const copyPw = () => {
    if (tempPassword) { navigator.clipboard.writeText(tempPassword); setCopied(true); setTimeout(() => setCopied(false), 2000); }
  };

  const closeModal = () => { setResetUser(null); setTempPassword(null); setCopied(false); };

  const roleLabel = (r: string) => r === 'group_leader' ? 'Group Leader' : r === 'gm' ? 'GM' : r.charAt(0).toUpperCase() + r.slice(1);

  return (
    <div className="max-w-4xl mx-auto">
      <h2 className="text-xl font-bold text-navy mb-4">Users</h2>
      <div className="bg-white rounded-xl border border-neutral-100 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-neutral-50 text-neutral-500 text-xs uppercase tracking-wider">
            <tr>
              <th className="text-left px-4 py-3">Name</th>
              <th className="text-left px-4 py-3">Email</th>
              <th className="text-left px-4 py-3">Role</th>
              <th className="text-left px-4 py-3">Status</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-neutral-50">
            {users.map(u => (
              <tr key={u.id} className="hover:bg-neutral-50/50">
                <td className="px-4 py-3 font-medium text-neutral-900">{u.name}</td>
                <td className="px-4 py-3 text-neutral-500">{u.email}</td>
                <td className="px-4 py-3"><span className="px-2 py-0.5 rounded-full text-xs font-medium bg-neutral-100 text-neutral-600">{roleLabel(u.role)}</span></td>
                <td className="px-4 py-3">
                  {u.must_reset_password && <span className="text-xs text-amber-600 font-medium">Reset pending</span>}
                </td>
                <td className="px-4 py-3 text-right">
                  {u.role !== 'admin' && (
                    <button onClick={() => setResetUser(u)}
                      className="text-xs text-primary hover:text-primary-dark font-medium">
                      Reset Password
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {resetUser && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50" onClick={closeModal}>
          <div className="bg-white rounded-xl shadow-xl w-full max-w-sm p-6" onClick={e => e.stopPropagation()}>
            {!tempPassword ? (
              <>
                <h3 className="text-lg font-bold text-navy mb-2">Reset Password</h3>
                <p className="text-sm text-neutral-600 mb-5">
                  Generate a temporary password for <span className="font-medium">{resetUser.name}</span>?
                  They will be required to set a new password on next login.
                </p>
                <div className="flex justify-end gap-2">
                  <button onClick={closeModal} className="px-4 py-2 text-sm text-neutral-600 hover:bg-neutral-50 rounded-lg">Cancel</button>
                  <button onClick={doReset} disabled={loading}
                    className="px-4 py-2 text-sm bg-primary text-white rounded-lg font-medium hover:bg-primary-dark disabled:opacity-50">
                    {loading ? 'Resetting…' : 'Reset'}
                  </button>
                </div>
              </>
            ) : (
              <>
                <h3 className="text-lg font-bold text-navy mb-2">Temporary Password</h3>
                <p className="text-sm text-neutral-600 mb-3">{resetUser.name}'s temporary password:</p>
                <div className="flex items-center gap-2 mb-3">
                  <code className="flex-1 bg-neutral-50 border border-neutral-200 rounded-lg px-3 py-2 text-sm font-mono tracking-wide select-all">{tempPassword}</code>
                  <button onClick={copyPw} className="px-3 py-2 text-sm bg-neutral-100 hover:bg-neutral-200 rounded-lg" title="Copy">
                    {copied ? '✓' : '📋'}
                  </button>
                </div>
                <p className="text-xs text-amber-600 mb-4">⚠ This will not be shown again. Share it securely with the user.</p>
                <div className="flex justify-end">
                  <button onClick={closeModal} className="px-4 py-2 text-sm bg-primary text-white rounded-lg font-medium hover:bg-primary-dark">Done</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
