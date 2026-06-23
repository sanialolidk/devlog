import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';
import type { Session } from '../types';

interface Props {
  sessions: Session[];
}

function elapsed(startTime: string) {
  const secs = Math.floor((Date.now() - new Date(startTime).getTime()) / 1000);
  const h = Math.floor(secs / 3600);
  const m = Math.floor((secs % 3600) / 60);
  return h ? `${h}h ${m}m` : `${m}m`;
}

function TagInput({ sessionId }: { sessionId: number }) {
  const [value, setValue] = useState('');
  const qc = useQueryClient();
  const tag = useMutation({
    mutationFn: (names: string[]) => api.tagSession(sessionId, names),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sessions'] });
      setValue('');
    },
  });

  const submit = () => {
    const names = value.split(',').map((s) => s.trim()).filter(Boolean);
    if (names.length) tag.mutate(names);
  };

  return (
    <div className="flex gap-1 mt-1">
      <input
        className="w-28 rounded border border-gray-200 px-2 py-0.5 text-xs focus:outline-none focus:ring-1 focus:ring-violet-400"
        placeholder="add tags…"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && submit()}
      />
      <button
        onClick={submit}
        className="text-xs text-violet-600 hover:text-violet-800"
      >
        +
      </button>
    </div>
  );
}

export function SessionList({ sessions }: Props) {
  if (sessions.length === 0) {
    return <p className="text-sm text-gray-400 py-8 text-center">No sessions yet. Start one above.</p>;
  }

  return (
    <div className="rounded-lg border border-gray-100 bg-white shadow-xs overflow-hidden">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-100 bg-gray-50 text-left text-xs text-gray-400 uppercase tracking-wide">
            <th className="px-4 py-3 w-8">#</th>
            <th className="px-4 py-3">Description</th>
            <th className="px-4 py-3">Started</th>
            <th className="px-4 py-3 text-right">Duration</th>
            <th className="px-4 py-3">Tags</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-50">
          {sessions.map((s) => (
            <tr key={s.id} className="hover:bg-gray-50 transition-colors">
              <td className="px-4 py-3 text-gray-300">{s.id}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2">
                  {s.is_active && (
                    <span className="h-2 w-2 rounded-full bg-green-400 animate-pulse flex-shrink-0" />
                  )}
                  <span className="font-medium text-gray-800">{s.description}</span>
                </div>
              </td>
              <td className="px-4 py-3 text-gray-400">
                {new Date(s.start_time).toLocaleString('en-US', {
                  month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
                })}
              </td>
              <td className="px-4 py-3 text-right font-mono text-gray-600">
                {s.is_active
                  ? <span className="text-green-600">{elapsed(s.start_time)}</span>
                  : `${s.duration_minutes ?? 0} min`}
              </td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1">
                  {s.tags.map((t) => (
                    <span key={t.id} className="rounded-full bg-violet-50 px-2 py-0.5 text-xs text-violet-600">
                      {t.name}
                    </span>
                  ))}
                </div>
                <TagInput sessionId={s.id} />
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
