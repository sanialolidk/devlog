import type { Session, Tag } from './types';

const BASE = 'http://localhost:8001';

function getToken() {
  return localStorage.getItem('devlog_token');
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(`${BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...init,
  });
  if (res.status === 401) {
    localStorage.removeItem('devlog_token');
    window.location.reload();
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail ?? `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  register: (email: string, password: string) =>
    req<{ access_token: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  login: (email: string, password: string) =>
    req<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

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
