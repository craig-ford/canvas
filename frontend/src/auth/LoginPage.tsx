import { useState, FormEvent } from 'react';
import { useAuth } from './useAuth';

export function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
    } catch {
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-ice font-sans">
      <div className="bg-white p-10 rounded-xl shadow-lg w-full max-w-sm border border-neutral-100">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-navy tracking-tight">Canvas</h1>
          <p className="text-sm text-neutral-500 mt-1">Portfolio Dashboard</p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="bg-warning-pale border border-warning-dark/30 text-neutral-800 text-sm rounded-lg px-4 py-2.5 text-center">
              {error}
            </div>
          )}
          <div>
            <label className="block text-sm font-medium text-neutral-800 mb-1.5">Email</label>
            <input
              type="email" value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-neutral-100 rounded-lg px-3.5 py-2.5 text-sm text-neutral-900 bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary placeholder:text-neutral-300"
              placeholder="you@volarisgroup.com" required autoFocus
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-neutral-800 mb-1.5">Password</label>
            <input
              type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-neutral-100 rounded-lg px-3.5 py-2.5 text-sm text-neutral-900 bg-neutral-50 focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary"
              required
            />
          </div>
          <button type="submit" disabled={loading}
            className="w-full bg-primary text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary disabled:opacity-50 transition-colors">
            {loading ? 'Signing in…' : 'Sign in'}
          </button>
        </form>
        <p className="text-xs text-neutral-400 text-center mt-4">Forgot password? Contact your administrator.</p>
      </div>
    </div>
  );
}
