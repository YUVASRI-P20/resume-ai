'use client';

import React, { useEffect, useState } from 'react';
import { apiClient } from '@/services/apiClient';
import { DashboardHeader } from '@/components/layout/DashboardHeader';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { Network, Loader2 } from 'lucide-react';

interface GraphNode {
  id: string;
  topic_name: string;
  category: string;
  mastery_score: number;
  status: string;
  is_strength: boolean;
  is_weakness: boolean;
}

export default function KnowledgeGraphPage() {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const { useAuthStore } = await import('@/store/useAuthStore');
        const userId = useAuthStore.getState().user?.id;
        if (!userId) {
          setError('Not signed in.');
          return;
        }
        const response = await apiClient.get(`/knowledge-graph/${userId}`);
        setNodes(response.data.nodes);
      } catch {
        setError('Could not load your knowledge graph.');
      } finally {
        setIsLoading(false);
      }
    })();
  }, []);

  return (
    <div className="flex-1 space-y-6 pb-12">
      <DashboardHeader
        title="Knowledge Graph"
        subtitle="Topic mastery computed from your real interview evaluations and coding submissions."
      />

      <main className="p-6 max-w-5xl mx-auto space-y-6">
        {isLoading ? (
          <div className="flex justify-center py-16">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : error ? (
          <Card className="p-8 text-center text-sm text-slate-600">{error}</Card>
        ) : nodes.length === 0 ? (
          <Card className="p-10 text-center space-y-2">
            <Network className="w-10 h-10 text-slate-300 mx-auto" />
            <p className="text-base font-semibold text-slate-700">No performance data yet</p>
            <p className="text-sm text-slate-500">
              Complete an interview or coding test — topic mastery is built from your actual results.
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {nodes.map((n) => (
              <Card key={n.id} className="p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold text-slate-900">{n.topic_name}</h3>
                  <Badge variant={n.is_strength ? 'success' : n.is_weakness ? 'error' : 'primary'}>
                    {n.status}
                  </Badge>
                </div>
                <ProgressBar
                  progress={n.mastery_score}
                  color={n.is_strength ? 'emerald' : n.is_weakness ? 'purple' : 'blue'}
                  showPercentage={false}
                />
                <span className="text-xs text-slate-500 font-mono">
                  Mastery: {Math.round(n.mastery_score)}%
                </span>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
