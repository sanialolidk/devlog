import type { Session } from '../types';

interface Props {
  sessions: Session[];
}

export function StatsPanel({ sessions }: Props) {
  const completed = sessions.filter((s) => s.end_time);
  const active = sessions.find((s) => s.is_active);
  const totalMin = completed.reduce((sum, s) => sum + (s.duration_minutes ?? 0), 0);
  const hours = Math.floor(totalMin / 60);
  const mins = Math.round(totalMin % 60);

  const tagCounts: Record<string, number> = {};
  for (const s of sessions) {
    for (const t of s.tags) {
      tagCounts[t.name] = (tagCounts[t.name] ?? 0) + 1;
    }
  }
  const topTags = Object.entries(tagCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5);

  const stats = [
    { label: 'Sessions', value: sessions.length },
    { label: 'Completed', value: completed.length },
    { label: 'Time logged', value: hours ? `${hours}h ${mins}m` : `${mins}m` },
  ];

  return (
    <div className="space-y-4">
      {active && (
        <div className="rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800">
          <span className="mr-2 inline-block h-2 w-2 rounded-full bg-green-500 animate-pulse" />
          Active: <span className="font-medium">{active.description}</span>
        </div>
      )}

      <div className="grid grid-cols-3 gap-3">
        {stats.map(({ label, value }) => (
          <div key={label} className="rounded-lg border border-gray-100 bg-white p-4 text-center shadow-xs">
            <p className="text-2xl font-semibold text-gray-800">{value}</p>
            <p className="text-xs text-gray-400 mt-0.5">{label}</p>
          </div>
        ))}
      </div>

      {topTags.length > 0 && (
        <div className="rounded-lg border border-gray-100 bg-white p-4 shadow-xs">
          <p className="mb-2 text-xs font-medium text-gray-400 uppercase tracking-wide">Top tags</p>
          <div className="flex flex-wrap gap-2">
            {topTags.map(([name, count]) => (
              <span
                key={name}
                className="rounded-full bg-violet-50 px-3 py-1 text-xs font-medium text-violet-700"
              >
                {name} <span className="opacity-60">×{count}</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
