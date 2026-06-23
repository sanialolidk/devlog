import { useQuery } from '@tanstack/react-query';
import { api } from './api';
import { StartSession } from './components/StartSession';
import { StatsPanel } from './components/StatsPanel';
import { ActivityChart } from './components/ActivityChart';
import { SessionList } from './components/SessionList';

function App() {
  const { data: sessions = [], isLoading, isError } = useQuery({
    queryKey: ['sessions'],
    queryFn: () => api.listSessions(),
  });

  return (
    <div className="min-h-screen bg-gray-50 font-sans">
      <header className="border-b border-gray-100 bg-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold text-violet-600">DevLog</span>
          <span className="text-xs text-gray-400 bg-gray-100 rounded px-2 py-0.5">dashboard</span>
        </div>
        {isLoading && <span className="text-xs text-gray-400 animate-pulse">Loading…</span>}
        {isError && <span className="text-xs text-red-400">Can't reach API — is it running on :8001?</span>}
      </header>

      <main className="mx-auto max-w-5xl px-6 py-8 space-y-6">
        <StartSession />
        <StatsPanel sessions={sessions} />
        <ActivityChart sessions={sessions} />
        <div>
          <h2 className="mb-3 text-sm font-medium text-gray-500 uppercase tracking-wide">
            Recent sessions
          </h2>
          <SessionList sessions={sessions} />
        </div>
      </main>
    </div>
  );
}

export default App;
