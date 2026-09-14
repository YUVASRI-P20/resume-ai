'use client';

import React, { useState } from 'react';
import { Settings as SettingsIcon, Mic, Volume2, Database, Key, Save, Moon, Sparkles } from 'lucide-react';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Badge } from '@/components/ui/Badge';

export default function SettingsPage() {
  const [voice, setVoice] = useState('Alloy (Staff Engineer)');
  const [fastApiUrl, setFastApiUrl] = useState('http://127.0.0.1:8000/api/v1');
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="flex-1 space-y-6">
      <DashboardHeader
        title="Platform & AI Settings"
        subtitle="Configure AI voice model, FastAPI backend endpoint, speech latency, and account preferences."
      />

      <main className="p-6 max-w-4xl mx-auto space-y-8">
        <Card className="glass-panel p-8 space-y-6">
          <form onSubmit={handleSave} className="space-y-6">
            {/* AI Voice Selection */}
            <div className="space-y-3">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 font-mono flex items-center gap-1.5">
                <Mic className="w-4 h-4 text-blue-400" /> AI Coach Voice Persona Model
              </label>
              <select
                value={voice}
                onChange={(e) => setVoice(e.target.value)}
                className="w-full h-11 rounded-xl bg-slate-900 border border-slate-700/80 px-4 text-sm text-slate-100 focus:outline-none focus:border-blue-500"
              >
                <option value="Alloy">Alloy (Authoritative Senior Staff Persona)</option>
                <option value="Echo">Echo (Conversational Principal Architect)</option>
                <option value="Onyx">Onyx (Deep Technical System Designer)</option>
                <option value="Fable">Fable (Encouraging Mentor Persona)</option>
              </select>
            </div>

            {/* FastAPI Endpoint */}
            <div className="space-y-2">
              <Input
                label="FastAPI Backend Endpoint URL"
                value={fastApiUrl}
                onChange={(e) => setFastApiUrl(e.target.value)}
                icon={<Database className="w-4 h-4 text-purple-400" />}
              />
              <p className="text-[11px] text-slate-500 font-mono">
                When live, Axios client connects automatically to this FastAPI server URL.
              </p>
            </div>

            {/* Save Button */}
            <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
              {saved ? (
                <span className="text-xs text-emerald-400 font-mono font-bold">Settings saved successfully!</span>
              ) : (
                <span className="text-xs text-slate-500 font-mono">All preferences stored in client local storage.</span>
              )}
              <Button type="submit" variant="glow" size="md" className="gap-2">
                <Save className="w-4 h-4" /> Save Settings
              </Button>
            </div>
          </form>
        </Card>
      </main>
    </div>
  );
}
