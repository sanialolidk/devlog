import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api';

export function StartSession() {
  const [description, setDescription] = useState('');
  const qc = useQueryClient();

  const start = useMutation({
    mutationFn: () => api.startSession(description.trim()),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sessions'] });
      setDescription('');
    },
  });

  const stop = useMutation({
    mutationFn: async () => {
      const sessions = await api.listSessions();
      const active = sessions.find((s) => s.is_active);
      if (!active) throw new Error('No active session');
      return api.stopSession(active.id);
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['sessions'] }),
  });

  return (
    <div className="flex gap-2">
      <input
        className="flex-1 rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-400"
        placeholder="What are you working on?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && description.trim() && start.mutate()}
      />
      <button
        onClick={() => start.mutate()}
        disabled={!description.trim() || start.isPending}
        className="rounded-lg bg-violet-600 px-4 py-2 text-sm font-medium text-white hover:bg-violet-700 disabled:opacity-40 transition-colors"
      >
        {start.isPending ? 'Starting…' : 'Start'}
      </button>
      <button
        onClick={() => stop.mutate()}
        disabled={stop.isPending}
        className="rounded-lg border border-gray-200 bg-white px-4 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 transition-colors"
      >
        {stop.isPending ? 'Stopping…' : 'Stop'}
      </button>
      {(start.isError || stop.isError) && (
        <p className="self-center text-sm text-red-500">
          {(start.error ?? stop.error)?.message}
        </p>
      )}
    </div>
  );
}
