import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import type { Session } from '../types';

interface Props {
  sessions: Session[];
}

function formatDay(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
}

export function ActivityChart({ sessions }: Props) {
  const byDay: Record<string, number> = {};

  for (let i = 6; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    byDay[d.toDateString()] = 0;
  }

  for (const s of sessions) {
    if (!s.duration_minutes) continue;
    const day = new Date(s.start_time).toDateString();
    if (day in byDay) {
      byDay[day] += s.duration_minutes / 60;
    }
  }

  const data = Object.entries(byDay).map(([day, hours]) => ({
    day: formatDay(new Date(day).toISOString()),
    hours: Math.round(hours * 10) / 10,
    isToday: day === new Date().toDateString(),
  }));

  return (
    <div className="rounded-lg border border-gray-100 bg-white p-4 shadow-xs">
      <p className="mb-3 text-xs font-medium text-gray-400 uppercase tracking-wide">Hours logged — last 7 days</p>
      <ResponsiveContainer width="100%" height={160}>
        <BarChart data={data} barSize={28}>
          <XAxis dataKey="day" tick={{ fontSize: 11, fill: '#9ca3af' }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: '#9ca3af' }} axisLine={false} tickLine={false} width={28} />
          <Tooltip
            formatter={(v: number) => [`${v}h`, 'Time']}
            contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #e5e7eb' }}
          />
          <Bar dataKey="hours" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.isToday ? '#7c3aed' : '#ddd6fe'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
