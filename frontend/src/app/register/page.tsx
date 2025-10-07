'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPost } from '@/lib/api';
import AuthShell from '@/components/AuthShell';

type User = { id: number; email: string; full_name?: string | null };

export default function RegisterPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await apiPost<User>('/auth/register', { email, full_name: fullName, password });
      router.replace('/login');
    } catch (err: any) {
      setError(err?.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell title="Create your account" subtitle="Join and explore the platform">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block mb-1 text-gray-700">Full name</label>
          <input
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            className="w-full rounded-xl px-3 py-3 text-gray-800 outline-none"
            style={{ background: '#ededed', boxShadow: 'inset 6px 6px 12px #d8d8d8, inset -6px -6px 12px #ffffff' }}
          />
        </div>
        <div>
          <label className="block mb-1 text-gray-700">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-xl px-3 py-3 text-gray-800 outline-none"
            style={{ background: '#ededed', boxShadow: 'inset 6px 6px 12px #d8d8d8, inset -6px -6px 12px #ffffff' }}
            required
          />
        </div>
        <div>
          <label className="block mb-1 text-gray-700">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-xl px-3 py-3 text-gray-800 outline-none"
            style={{ background: '#ededed', boxShadow: 'inset 6px 6px 12px #d8d8d8, inset -6px -6px 12px #ffffff' }}
            required
            minLength={8}
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          type="submit"
          className="w-full py-3 rounded-xl font-semibold text-white"
          style={{ background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)', boxShadow: '8px 8px 16px #6b5acc, -8px -8px 16px #8b79f0' }}
          disabled={loading}
        >
          {loading ? 'Creating account...' : 'Create account'}
        </button>
        <div className="text-center text-sm text-gray-600">
          Already have an account? <a href="/login" className="underline">Sign in</a>
        </div>
      </form>
    </AuthShell>
  );
}


