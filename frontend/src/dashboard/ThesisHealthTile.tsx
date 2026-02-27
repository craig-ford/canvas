import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiClient } from '../api/client';

type Status = 'observed' | 'not_observed' | 'in_progress' | 'not_started' | 'stalled';

interface PPInfo { id: string; status: Status; description: string }

interface ThesisHealth {
  vbu_id: string;
  vbu_name: string;
  thesis_id: string;
  thesis_order: number;
  thesis_text: string;
  category_name: string | null;
  category_color: string | null;
  observed: number;
  not_observed: number;
  total_scored: number;
  total_proof_points: number;
  signal: 'strengthening' | 'weakening' | 'neutral';
  proof_points: PPInfo[];
}

const statusColors: Record<Status, { bg: string; label: string }> = {
  observed:     { bg: 'bg-green-500',  label: 'Observed' },
  not_observed: { bg: 'bg-red-400',    label: 'Not Observed' },
  in_progress:  { bg: 'bg-blue-400',   label: 'In Progress' },
  not_started:  { bg: 'bg-gray-300',   label: 'Not Started' },
  stalled:      { bg: 'bg-amber-400',  label: 'Stalled' },
};

const statusOrder: Status[] = ['observed', 'in_progress', 'not_started', 'stalled', 'not_observed'];

const signalConfig = {
  strengthening: { icon: '▲', color: 'text-green-600', label: 'Strengthening' },
  weakening:     { icon: '▼', color: 'text-red-600',   label: 'Weakening' },
  neutral:       { icon: '—', color: 'text-gray-400',  label: 'Neutral' },
};

function groupByStatus(pps: PPInfo[]): { status: Status; pps: PPInfo[] }[] {
  const map = new Map<Status, PPInfo[]>();
  for (const pp of pps) {
    const s = pp.status as Status;
    if (!map.has(s)) map.set(s, []);
    map.get(s)!.push(pp);
  }
  return statusOrder.filter(s => map.has(s)).map(s => ({ status: s, pps: map.get(s)! }));
}

function ClickableBar({ groups, total, vbuId, navigate }: {
  groups: { status: Status; pps: PPInfo[] }[];
  total: number;
  vbuId: string;
  navigate: (path: string) => void;
}) {
  if (total === 0) return <div className="h-4 w-full bg-gray-100 rounded-full" />;
  return (
    <div className="h-4 w-full bg-gray-100 rounded-full overflow-hidden flex">
      {groups.map(({ status, pps }) => {
        const pct = (pps.length / total) * 100;
        const cfg = statusColors[status];
        return (
          <div
            key={status}
            className={`${cfg.bg} h-full cursor-pointer hover:brightness-110 transition-all relative group`}
            style={{ width: `${pct}%` }}
            title={`${cfg.label}: ${pps.length} proof point${pps.length !== 1 ? 's' : ''} — click to view`}
            onClick={() => navigate(`/vbus/${vbuId}/canvas#pp-${pps[0].id}`)}
          >
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 hidden group-hover:block z-10 bg-gray-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap pointer-events-none">
              {cfg.label} ({pps.length})
            </div>
          </div>
        );
      })}
    </div>
  );
}

export const ThesisHealthTile: React.FC<{ vbuIds?: string[] }> = ({ vbuIds = [] }) => {
  const navigate = useNavigate();
  const [items, setItems] = useState<ThesisHealth[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient.get<{ data: ThesisHealth[] }>('/portfolio/thesis-health')
      .then(res => setItems(res.data.data))
      .catch(() => setError('Failed to load thesis health data'))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="space-y-6">
        {[1, 2].map(i => (
          <div key={i} className="bg-white rounded-lg border border-neutral-100 p-6 animate-pulse">
            <div className="h-4 bg-neutral-100 rounded w-1/3 mb-4" />
            <div className="h-4 bg-neutral-100 rounded w-2/3" />
          </div>
        ))}
      </div>
    );
  }

  if (error) return <div className="bg-white rounded-lg border border-neutral-100 p-6 text-sm text-red-600">{error}</div>;
  if (items.length === 0) return null;

  // Apply VBU filter
  const filtered = vbuIds.length > 0 ? items.filter(i => vbuIds.includes(i.vbu_id)) : items;
  if (filtered.length === 0) return null;

  // Build VBU aggregates
  const vbuMap = new Map<string, { vbu_id: string; vbu_name: string; pps: PPInfo[] }>();
  for (const item of filtered) {
    let agg = vbuMap.get(item.vbu_id);
    if (!agg) {
      agg = { vbu_id: item.vbu_id, vbu_name: item.vbu_name, pps: [] };
      vbuMap.set(item.vbu_id, agg);
    }
    agg.pps.push(...item.proof_points);
  }
  const aggregates = Array.from(vbuMap.values());

  return (
    <div className="space-y-6">
      {/* Section 1: Overall VBU Proof Point Trend */}
      <div className="bg-white rounded-lg border border-neutral-100 p-6" role="region" aria-label="Portfolio proof point overview">
        <h2 className="text-lg font-semibold text-navy mb-4">Proof Point Overview</h2>
        <div className="space-y-3">
          {aggregates.map(agg => {
            const groups = groupByStatus(agg.pps);
            return (
              <div key={agg.vbu_id} className="flex items-center gap-3">
                <span className="text-sm font-medium text-gray-700 w-32 shrink-0 truncate" title={agg.vbu_name}>{agg.vbu_name}</span>
                <div className="flex-1">
                  <ClickableBar groups={groups} total={agg.pps.length} vbuId={agg.vbu_id} navigate={navigate} />
                </div>
                <span className="text-xs text-gray-500 w-10 text-right shrink-0">{agg.pps.length}</span>
              </div>
            );
          })}
        </div>
        <div className="flex flex-wrap gap-3 mt-3 text-xs text-gray-400">
          {statusOrder.map(s => (
            <span key={s} className="flex items-center gap-1">
              <span className={`inline-block w-3 h-3 rounded ${statusColors[s].bg}`} />
              {statusColors[s].label}
            </span>
          ))}
        </div>
      </div>

      {/* Section 2: Thesis Detail Table */}
      <div className="bg-white rounded-lg border border-neutral-100 p-6" role="region" aria-label="Thesis detail">
        <h2 className="text-lg font-semibold text-navy mb-4">Thesis Detail</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-neutral-100 text-left text-xs text-gray-500 uppercase tracking-wider">
                <th className="pb-2 pr-3 font-medium">VBU</th>
                <th className="pb-2 pr-3 font-medium">Thesis</th>
                <th className="pb-2 pr-3 font-medium w-28">Category</th>
                <th className="pb-2 pr-3 font-medium w-48">Proof Points</th>
                <th className="pb-2 pr-3 font-medium text-center w-16">Signal</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(t => {
                const cfg = signalConfig[t.signal];
                const groups = groupByStatus(t.proof_points);
                return (
                  <tr key={t.thesis_id} className="border-b border-neutral-50 hover:bg-gray-50">
                    <td className="py-2 pr-3 text-gray-600 whitespace-nowrap">{t.vbu_name}</td>
                    <td className="py-2 pr-3 text-gray-800 max-w-xs truncate" title={t.thesis_text}>
                      {t.thesis_order}. {t.thesis_text}
                    </td>
                    <td className="py-2 pr-3 whitespace-nowrap">
                      {t.category_name
                        ? (() => {
                            const [bg, fg] = (t.category_color || '').split(',');
                            return <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium" style={{ backgroundColor: bg || '#f3f4f6', color: fg || '#6b7280' }}>{t.category_name}</span>;
                          })()
                        : <span className="text-gray-400 text-xs">—</span>
                      }
                    </td>
                    <td className="py-2 pr-3">
                      <div className="flex items-center gap-2">
                        <div className="flex-1">
                          <ClickableBar groups={groups} total={t.proof_points.length} vbuId={t.vbu_id} navigate={navigate} />
                        </div>
                        <span className="text-xs text-gray-400 shrink-0 w-8 text-right">{t.proof_points.length}</span>
                      </div>
                    </td>
                    <td className="py-2 text-center">
                      <span className={`text-sm font-semibold ${cfg.color}`} title={cfg.label}>{cfg.icon}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
