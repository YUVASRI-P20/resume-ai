'use client';

import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import {
  Network,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  BrainCircuit,
  Search,
  ZoomIn,
  ZoomOut,
  RotateCcw,
  BookOpen,
  Filter,
  CheckCircle2,
  Cpu,
  Layers,
  Activity,
  Plus,
  Play,
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { ProgressBar } from '@/components/ui/ProgressBar';
import { KnowledgeGraphNode } from '@/types/roadmap';
import { MOCK_ROADMAP } from '@/constants/mockData';

const CATEGORY_COLORS: Record<string, { stroke: string; bg: string; fill: string; text: string; ring: string }> = {
  Frontend: { stroke: '#3B82F6', bg: 'bg-blue-950/70', fill: '#3B82F6', text: 'text-blue-400', ring: 'ring-blue-500' },
  Backend: { stroke: '#10B981', bg: 'bg-emerald-950/70', fill: '#10B981', text: 'text-emerald-400', ring: 'ring-emerald-500' },
  'System Design': { stroke: '#A855F7', bg: 'bg-purple-950/70', fill: '#A855F7', text: 'text-purple-400', ring: 'ring-purple-500' },
  Algorithms: { stroke: '#F59E0B', bg: 'bg-amber-950/70', fill: '#F59E0B', text: 'text-amber-400', ring: 'ring-amber-500' },
  Security: { stroke: '#EF4444', bg: 'bg-red-950/70', fill: '#EF4444', text: 'text-red-400', ring: 'ring-red-500' },
  'DevOps & Cloud': { stroke: '#06B6D4', bg: 'bg-cyan-950/70', fill: '#06B6D4', text: 'text-cyan-400', ring: 'ring-cyan-500' },
};

interface PositionedNode extends KnowledgeGraphNode {
  posX: number;
  posY: number;
}

export function InteractiveKnowledgeGraph() {
  const router = useRouter();
  const [nodes, setNodes] = useState<PositionedNode[]>(() =>
    MOCK_ROADMAP.graphNodes.map((n, idx) => ({
      ...n,
      posX: n.x || 150 + (idx % 4) * 220,
      posY: n.y || 100 + Math.floor(idx / 4) * 160,
    }))
  );

  const [selectedNodeId, setSelectedNodeId] = useState<string>(MOCK_ROADMAP.graphNodes[0].id);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [statusFilter, setStatusFilter] = useState<string>('All');
  const [zoomLevel, setZoomLevel] = useState<number>(1);
  const [panOffset, setPanOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Dragging state
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);
  const [isPanning, setIsPanning] = useState(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const svgRef = useRef<SVGSVGElement | null>(null);

  const selectedNode = useMemo(() => {
    return nodes.find((n) => n.id === selectedNodeId) || nodes[0];
  }, [nodes, selectedNodeId]);

  // Extract unique categories
  const categories = useMemo(() => {
    const set = new Set(nodes.map((n) => n.category));
    return ['All', ...Array.from(set)];
  }, [nodes]);

  // Connected node IDs for highlighted paths
  const connectedNodeIds = useMemo(() => {
    if (!selectedNode) return new Set<string>();
    const set = new Set<string>();
    set.add(selectedNode.id);
    selectedNode.connections.forEach((id) => set.add(id));
    nodes.forEach((n) => {
      if (n.connections.includes(selectedNode.id)) {
        set.add(n.id);
      }
    });
    return set;
  }, [selectedNode, nodes]);

  // Filtered nodes
  const filteredNodes = useMemo(() => {
    return nodes.filter((n) => {
      const matchCat = selectedCategory === 'All' || n.category === selectedCategory;
      const matchStatus = statusFilter === 'All' || n.status === statusFilter;
      const matchSearch =
        !searchQuery ||
        n.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        n.category.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCat && matchStatus && matchSearch;
    });
  }, [nodes, selectedCategory, statusFilter, searchQuery]);

  // SVG Mouse handlers for Dragging Nodes & Canvas Panning
  const handleMouseDownNode = (e: React.MouseEvent, nodeId: string) => {
    e.stopPropagation();
    setSelectedNodeId(nodeId);
    setDraggingNodeId(nodeId);
    setDragStart({ x: e.clientX, y: e.clientY });
  };

  const handleMouseDownCanvas = (e: React.MouseEvent) => {
    if (e.button === 0) {
      setIsPanning(true);
      setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
    }
  };

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (draggingNodeId) {
        const dx = (e.clientX - dragStart.x) / zoomLevel;
        const dy = (e.clientY - dragStart.y) / zoomLevel;
        setNodes((prev) =>
          prev.map((n) => {
            if (n.id === draggingNodeId) {
              return { ...n, posX: Math.max(40, n.posX + dx), posY: Math.max(40, n.posY + dy) };
            }
            return n;
          })
        );
        setDragStart({ x: e.clientX, y: e.clientY });
      } else if (isPanning) {
        setPanOffset({
          x: e.clientX - dragStart.x,
          y: e.clientY - dragStart.y,
        });
      }
    },
    [draggingNodeId, isPanning, dragStart, zoomLevel]
  );

  const handleMouseUp = () => {
    setDraggingNodeId(null);
    setIsPanning(false);
  };

  const handleResetView = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
    // Reset positions to default layout
    setNodes(
      MOCK_ROADMAP.graphNodes.map((n, idx) => ({
        ...n,
        posX: n.x || 150 + (idx % 4) * 220,
        posY: n.y || 100 + Math.floor(idx / 4) * 160,
      }))
    );
  };

  const handlePracticeTopic = () => {
    if (selectedNode) {
      router.push('/dashboard/interview-setup');
    }
  };

  // Build edge connection lines
  const edges = useMemo(() => {
    const list: { from: PositionedNode; to: PositionedNode; isSelected: boolean; id: string }[] = [];
    const nodeMap = new Map<string, PositionedNode>();
    nodes.forEach((n) => nodeMap.set(n.id, n));

    nodes.forEach((node) => {
      node.connections.forEach((targetId) => {
        const target = nodeMap.get(targetId);
        if (target && node.id < target.id) {
          const isSelected =
            node.id === selectedNodeId ||
            target.id === selectedNodeId ||
            (connectedNodeIds.has(node.id) && connectedNodeIds.has(target.id));
          list.push({
            id: `${node.id}-${target.id}`,
            from: node,
            to: target,
            isSelected,
          });
        }
      });
    });
    return list;
  }, [nodes, selectedNodeId, connectedNodeIds]);

  const getStatusBadge = (status: KnowledgeGraphNode['status']) => {
    if (status === 'Strong') return <Badge variant="success">Strong Mastery (&gt;85%)</Badge>;
    if (status === 'Needs Improvement') return <Badge variant="warning">Needs Practice (70-85%)</Badge>;
    return <Badge variant="error">Weak Concept (&lt;70%)</Badge>;
  };

  return (
    <div className="space-y-6">
      {/* Top Filter & Toolbar */}
      <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4 p-4 rounded-2xl glass-panel bg-slate-900/80 border border-slate-800 backdrop-blur-xl">
        {/* Search & Domain Categories */}
        <div className="flex items-center flex-wrap gap-2">
          <div className="relative min-w-[220px]">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search concepts, Redis, Fiber..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700/80 rounded-xl pl-9 pr-3 py-1.5 text-xs text-slate-100 focus:outline-none focus:border-blue-500 font-sans"
            />
          </div>

          <div className="flex items-center gap-1 overflow-x-auto pb-1 lg:pb-0 scrollbar-none">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setSelectedCategory(cat)}
                className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all shrink-0 ${
                  selectedCategory === cat
                    ? 'bg-blue-600 text-white font-bold shadow-md shadow-blue-500/20'
                    : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Status Filters & Zoom Controls */}
        <div className="flex items-center justify-between lg:justify-end gap-3 font-mono text-xs">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-xl px-3 py-1.5 text-xs text-slate-300 focus:outline-none"
          >
            <option value="All">All Mastery Levels</option>
            <option value="Strong">Strong (&gt;85%)</option>
            <option value="Needs Improvement">Needs Practice (70-85%)</option>
            <option value="Weak">Weak (&lt;70%)</option>
          </select>

          <div className="flex items-center bg-slate-950 border border-slate-800 rounded-xl p-1 gap-1">
            <button
              type="button"
              onClick={() => setZoomLevel((z) => Math.min(1.6, z + 0.15))}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <span className="text-[11px] px-1 text-slate-300 font-bold">{Math.round(zoomLevel * 100)}%</span>
            <button
              type="button"
              onClick={() => setZoomLevel((z) => Math.max(0.6, z - 0.15))}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={handleResetView}
              className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              title="Reset Layout & Positions"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Interactive SVG Physics Canvas */}
        <Card className="lg:col-span-8 p-0 min-h-[580px] h-[640px] relative overflow-hidden bg-slate-950 border border-slate-800 shadow-2xl flex flex-col justify-between select-none">
          {/* Subtle Grid Background Pattern */}
          <div
            className="absolute inset-0 opacity-20 pointer-events-none"
            style={{
              backgroundImage: 'radial-gradient(#3B82F6 1px, transparent 1px)',
              backgroundSize: '24px 24px',
            }}
          />

          {/* Interactive SVG Layer */}
          <svg
            ref={svgRef}
            className="w-full h-full cursor-grab active:cursor-grabbing relative z-10"
            onMouseDown={handleMouseDownCanvas}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
          >
            <g transform={`translate(${panOffset.x}, ${panOffset.y}) scale(${zoomLevel})`}>
              {/* Dynamic Connection Lines with Pulsing Particles */}
              {edges.map((edge) => {
                const strokeColor = edge.isSelected ? '#60A5FA' : '#334155';
                const strokeWidth = edge.isSelected ? 2.5 : 1.5;
                const strokeDash = edge.isSelected ? 'none' : '4 4';

                // Midpoint for curve
                const mx = (edge.from.posX + edge.to.posX) / 2;
                const my = (edge.from.posY + edge.to.posY) / 2 - 15;

                return (
                  <g key={edge.id}>
                    <path
                      d={`M ${edge.from.posX} ${edge.from.posY} Q ${mx} ${my} ${edge.to.posX} ${edge.to.posY}`}
                      stroke={strokeColor}
                      strokeWidth={strokeWidth}
                      strokeDasharray={strokeDash}
                      fill="none"
                      className="transition-colors duration-300"
                    />

                    {/* Animated Energy Particle flowing along active edge */}
                    {edge.isSelected && (
                      <circle r="3" fill="#93C5FD">
                        <animateMotion
                          path={`M ${edge.from.posX} ${edge.from.posY} Q ${mx} ${my} ${edge.to.posX} ${edge.to.posY}`}
                          dur="2.5s"
                          repeatCount="indefinite"
                        />
                      </circle>
                    )}
                  </g>
                );
              })}

              {/* Interactive Node Circles */}
              {nodes.map((node) => {
                const isSelected = selectedNodeId === node.id;
                const isConnected = connectedNodeIds.has(node.id);
                const isFilteredOut = !filteredNodes.some((fn) => fn.id === node.id);
                const categoryStyle = CATEGORY_COLORS[node.category] || CATEGORY_COLORS.Frontend;

                // Mastery ring calculation
                const radius = 28;
                const circumference = 2 * Math.PI * radius;
                const strokeDashoffset = circumference - (node.masteryPercentage / 100) * circumference;

                return (
                  <g
                    key={node.id}
                    transform={`translate(${node.posX}, ${node.posY})`}
                    onMouseDown={(e) => handleMouseDownNode(e, node.id)}
                    className="cursor-pointer group"
                    opacity={isFilteredOut ? 0.2 : isSelected || isConnected ? 1 : 0.6}
                  >
                    {/* Outer Glowing Halo on Selection */}
                    {isSelected && (
                      <circle
                        r="38"
                        fill="none"
                        stroke={categoryStyle.stroke}
                        strokeWidth="2"
                        className="animate-ping opacity-30"
                      />
                    )}

                    {/* Base Node Circle */}
                    <circle
                      r={radius}
                      fill="#090D16"
                      stroke="#1E293B"
                      strokeWidth="3"
                      className="shadow-xl"
                    />

                    {/* Mastery Score Progress Ring */}
                    <circle
                      r={radius}
                      fill="none"
                      stroke={
                        node.status === 'Strong'
                          ? '#10B981'
                          : node.status === 'Needs Improvement'
                          ? '#F59E0B'
                          : '#EF4444'
                      }
                      strokeWidth="3"
                      strokeDasharray={circumference}
                      strokeDashoffset={strokeDashoffset}
                      strokeLinecap="round"
                      transform="rotate(-90)"
                      className="transition-all duration-500"
                    />

                    {/* Mastery Text inside node */}
                    <text
                      textAnchor="middle"
                      dy="4"
                      fill="#FFFFFF"
                      fontSize="11"
                      fontWeight="bold"
                      fontFamily="monospace"
                    >
                      {node.masteryPercentage}%
                    </text>

                    {/* Node Title Box Below */}
                    <g transform="translate(0, 42)">
                      <rect
                        x="-70"
                        y="0"
                        width="140"
                        height="24"
                        rx="8"
                        fill="#0F172A"
                        stroke={isSelected ? categoryStyle.stroke : '#334155'}
                        strokeWidth={isSelected ? '1.5' : '1'}
                      />
                      <text
                        textAnchor="middle"
                        dy="15"
                        fill="#F8FAFC"
                        fontSize="10"
                        fontWeight="600"
                        fontFamily="sans-serif"
                      >
                        {node.label.length > 20 ? `${node.label.substring(0, 18)}...` : node.label}
                      </text>
                    </g>
                  </g>
                );
              })}
            </g>
          </svg>

          {/* Canvas Bottom Legend & Quick Stats */}
          <div className="absolute bottom-4 left-4 right-4 z-20 flex flex-wrap items-center justify-between gap-3 p-3 rounded-xl bg-slate-900/90 border border-slate-800 backdrop-blur-md text-xs font-mono">
            <div className="flex items-center space-x-4">
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" /> Strong (&gt;85%)
              </span>
              <span className="flex items-center gap-1.5 text-amber-400">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" /> Needs Review (70-85%)
              </span>
              <span className="flex items-center gap-1.5 text-red-400">
                <span className="w-2.5 h-2.5 rounded-full bg-red-500" /> Weak Concept (&lt;70%)
              </span>
            </div>

            <span className="text-slate-400">
              Interactive Nodes: <strong className="text-white">{filteredNodes.length} Concepts</strong> • Click & Drag to reposition
            </span>
          </div>
        </Card>

        {/* Selected Node Details & Action Sidebar */}
        <Card className="lg:col-span-4 p-6 space-y-6 flex flex-col justify-between bg-slate-900/90 border-slate-800 glass-panel shadow-2xl">
          <div className="space-y-5">
            {/* Category & Mastery Badge */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <Badge variant="primary" className="font-mono text-xs">
                {selectedNode.category}
              </Badge>
              {getStatusBadge(selectedNode.status)}
            </div>

            {/* Title & Description */}
            <div className="space-y-2">
              <h3 className="text-xl font-extrabold text-white tracking-tight leading-snug">
                {selectedNode.label}
              </h3>
              <p className="text-xs text-slate-300 leading-relaxed">
                {selectedNode.description || 'Mastery calculated across technical interview responses, code submissions, and architectural deep-dives.'}
              </p>
            </div>

            {/* Mastery Meter */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
              <div className="flex justify-between items-center text-xs font-mono">
                <span className="text-slate-400">Concept Mastery:</span>
                <span className="font-bold text-blue-400 text-sm">{selectedNode.masteryPercentage}%</span>
              </div>
              <ProgressBar progress={selectedNode.masteryPercentage} color="blue" showPercentage={false} />
            </div>

            {/* Prerequisites */}
            {selectedNode.prerequisites && selectedNode.prerequisites.length > 0 && (
              <div className="space-y-2 text-xs">
                <span className="text-[10px] uppercase font-mono text-amber-400 font-bold block flex items-center gap-1">
                  <Layers className="w-3 h-3" /> Core Prerequisites
                </span>
                <div className="flex flex-wrap gap-1.5">
                  {selectedNode.prerequisites.map((req) => (
                    <span key={req} className="px-2.5 py-1 rounded-lg bg-slate-950 border border-slate-800 text-slate-200 font-mono text-[11px]">
                      {req}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Connected Topology Topics */}
            <div className="space-y-2 text-xs">
              <span className="text-[10px] uppercase font-mono text-purple-400 font-bold block flex items-center gap-1">
                <Network className="w-3 h-3" /> Interconnected Dependency Tree
              </span>
              <div className="flex flex-wrap gap-1.5">
                {selectedNode.connections.map((connId) => {
                  const target = nodes.find((n) => n.id === connId);
                  return (
                    <button
                      key={connId}
                      type="button"
                      onClick={() => setSelectedNodeId(connId)}
                      className="px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-800 border border-slate-800 hover:border-blue-500 text-blue-300 font-mono text-[11px] transition-colors"
                    >
                      {target?.label || connId} &rarr;
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Recommended Interview Questions */}
            {selectedNode.recommendedQuestions && selectedNode.recommendedQuestions.length > 0 && (
              <div className="space-y-2 text-xs">
                <span className="text-[10px] uppercase font-mono text-blue-400 font-bold block flex items-center gap-1">
                  <BookOpen className="w-3 h-3" /> Targeted Interview Questions
                </span>
                <ul className="space-y-1.5">
                  {selectedNode.recommendedQuestions.map((q, i) => (
                    <li key={i} className="p-2 rounded-lg bg-slate-950/80 border border-slate-800 text-[11px] text-slate-300 flex items-start gap-2">
                      <span className="text-blue-400 font-mono font-bold">•</span>
                      <span>{q}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Action Launchers */}
          <div className="pt-4 border-t border-slate-800 space-y-2.5">
            <Button
              variant="glow"
              size="md"
              className="w-full gap-2 text-xs font-mono shadow-xl"
              onClick={handlePracticeTopic}
            >
              <Play className="w-3.5 h-3.5" />
              <span>Practice Questions for this Topic</span>
              <ArrowRight className="w-3.5 h-3.5 ml-auto" />
            </Button>

            <Button
              variant="outline"
              size="sm"
              className="w-full gap-2 text-xs font-mono"
              onClick={() => router.push('/dashboard/roadmap')}
            >
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>View in Weekly Learning Roadmap</span>
            </Button>
          </div>
        </Card>
      </div>
    </div>
  );
}
