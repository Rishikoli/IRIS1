'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiPostForm } from '@/lib/api';
import AuthShell from '@/components/AuthShell';

type Token = { access_token: string; token_type: string };

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const form = new URLSearchParams();
      form.set('username', email);
      form.set('password', password);
      const token = await apiPostForm<Token>('/auth/login', form);
      if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', token.access_token);
      }
      router.replace('/');
    } catch (err: any) {
      setError(err?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthShell title="Welcome back" subtitle="Sign in to continue">
      <form onSubmit={onSubmit} className="space-y-4">
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
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          type="submit"
          className="w-full py-3 rounded-xl font-semibold text-white"
          style={{ background: 'linear-gradient(135deg, #7B68EE 0%, #6A5ACD 100%)', boxShadow: '8px 8px 16px #6b5acc, -8px -8px 16px #8b79f0' }}
          disabled={loading}
        >
          {loading ? 'Signing in...' : 'Sign in'}
        </button>
        <div className="text-center text-sm text-gray-600">
          Don&apos;t have an account? <a href="/register" className="underline">Register</a>
        </div>
      </form>
    </AuthShell>
  );
}


