'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Cpu, ArrowRight, Lock, Mail, User, UserCheck, Briefcase, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { useAuthStore } from '@/store/useAuthStore';
import { getApiErrorMessage } from '@/services/apiClient';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuthStore();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [accountType, setAccountType] = useState<'candidate' | 'recruiter'>('candidate');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    try {
      await register({
        name,
        email,
        password,
        role: accountType === 'recruiter' ? 'RECRUITER' : 'STUDENT',
      });
      router.push('/onboarding');
    } catch (err) {
      setError(getApiErrorMessage(err, 'Registration failed. Please check your details and try again.'));
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md relative z-10 space-y-6">
        <div className="text-center space-y-2">
          <Link href="/" className="inline-flex items-center space-x-3">
            <div className="h-12 w-12 rounded-2xl bg-blue-600 shadow-md flex items-center justify-center">
              <Cpu className="h-6 w-6 text-white" />
            </div>
          </Link>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">Create your account</h1>
          <p className="text-sm text-slate-500">Register as a candidate or recruiter</p>
        </div>

        <Card className="p-6 sm:p-8 space-y-5 bg-white border-slate-200 shadow-sm">
          {error && (
            <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-xs text-red-700 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
              <span>{error}</span>
            </div>
          )}

          {/* Account Type Selector */}
          <div className="grid grid-cols-2 gap-3">
            <button
              type="button"
              onClick={() => setAccountType('candidate')}
              className={`p-3 rounded-xl border text-left flex items-center gap-3 transition-all ${
                accountType === 'candidate'
                  ? 'bg-blue-50 border-blue-400 ring-1 ring-blue-200 text-slate-900'
                  : 'bg-white border-slate-200 text-slate-500'
              }`}
            >
              <UserCheck className="w-4 h-4 text-blue-600 shrink-0" />
              <div>
                <span className="text-xs font-bold block">Candidate</span>
                <span className="text-[10px] text-slate-500">Practice interviews</span>
              </div>
            </button>

            <button
              type="button"
              onClick={() => setAccountType('recruiter')}
              className={`p-3 rounded-xl border text-left flex items-center gap-3 transition-all ${
                accountType === 'recruiter'
                  ? 'bg-blue-50 border-blue-400 ring-1 ring-blue-200 text-slate-900'
                  : 'bg-white border-slate-200 text-slate-500'
              }`}
            >
              <Briefcase className="w-4 h-4 text-blue-600 shrink-0" />
              <div>
                <span className="text-xs font-bold block">Recruiter</span>
                <span className="text-[10px] text-slate-500">Screen candidates</span>
              </div>
            </button>
          </div>

          <form onSubmit={handleRegister} className="space-y-4">
            <Input
              label="Full Name"
              placeholder="Jane Doe"
              value={name}
              onChange={(e) => setName(e.target.value)}
              icon={<User className="w-4 h-4" />}
              minLength={2}
              required
            />

            <Input
              label="Email"
              type="email"
              placeholder="jane@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              icon={<Mail className="w-4 h-4" />}
              autoComplete="email"
              required
            />

            <Input
              label="Password"
              type="password"
              placeholder="Min 8 chars, upper + lower + digit"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              icon={<Lock className="w-4 h-4" />}
              autoComplete="new-password"
              minLength={8}
              required
            />
            <p className="text-[11px] text-slate-400 -mt-2">
              At least 8 characters with one uppercase letter, one lowercase letter and one digit.
            </p>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full gap-2 mt-3"
              isLoading={isLoading}
              loadingText="Creating account..."
            >
              <span>Create Account</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </form>
        </Card>

        <p className="text-center text-sm text-slate-500">
          Already have an account?{' '}
          <Link href="/login" className="font-semibold text-blue-600 hover:text-blue-700">
            Sign in &rarr;
          </Link>
        </p>
      </div>
    </div>
  );
}
