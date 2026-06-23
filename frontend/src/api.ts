import type { Session, Tag } from './types';

const BASE = 'http://localhost:8001';

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  listSessions: (all = true) =>
    req<Session[]>(`/sessions?all=${all}`),

  getSession: (id: number) =>
    req<Session>(`/sessions/${id}`),

  startSession: (description: string) =>
    req<Session>('/sessions', {
      method: 'POST',
      body: JSON.stringify({ description }),
    }),

  stopSession: (id: number) =>
    req<Session>(`/sessions/${id}/stop`, { method: 'PATCH' }),

  tagSession: (id: number, names: string[]) =>
    req<Session>(`/sessions/${id}/tags`, {
      method: 'POST',
      body: JSON.stringify({ names }),
    }),

  listTags: () =>
    req<Tag[]>('/tags'),
};
