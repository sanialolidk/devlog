import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { api } from './api';
import { AuthForm } from './components/AuthForm';
import { StartSession } from './components/StartSession';
import { StatsPanel } from './components/StatsPanel';
import { ActivityChart } from './components/ActivityChart';
import { SessionList } from './components/SessionList';

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('devlog_token'));
  const qc = useQueryClient();

  const handleAuth = (t: string) => {
    localStorage.setItem('devlog_token', t);
    setToken(t);
  };

  const handleLogout = () => {
    localStorage.removeItem('devlog_token');
    setToken(null);
    qc.clear();
  };

  if (!token) {
    return <AuthForm onAuth={handleAuth} />;
  }

  return <Dashboard onLogout={handleLogout} />;
}

function Dashboard({ onLogout }: { onLogout: () => void }) {
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
        <div className="flex items-center gap-4">
          {isLoading && <span className="text-xs text-gray-400 animate-pulse">Loading…</span>}
          {isError && <span className="text-xs text-red-400">Can't reach API</span>}
          <button
            onClick={onLogout}
            className="text-xs text-gray-400 hover:text-gray-600 transition-colors"
          >
            Sign out
          </button>
        </div>
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
