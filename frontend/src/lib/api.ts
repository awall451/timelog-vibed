const BASE = 'http://localhost:8888';

export interface Entry {
  id: number;
  project: string;
  category: string;
  description: string;
  hours: number;
  date: string;
}

export interface ProjectSum {
  project: string;
  hours: number;
}

export interface CategorySum {
  category: string;
  hours: number;
}

export interface NewEntry {
  project: string;
  category: string;
  description: string;
  hours: number;
  date?: string;
}

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  entries: {
    all: ()              => get<Entry[]>('/entries'),
    today: ()            => get<Entry[]>('/entries/today'),
    yesterday: ()        => get<Entry[]>('/entries/yesterday'),
    last: ()             => get<Entry>('/entries/last'),
    byMonth: (m: string) => get<Entry[]>(`/entries/month/${m}`),
    byProject: (n: string) => get<Entry[]>(`/entries/project/${encodeURIComponent(n)}`),
    byCategory: (n: string) => get<Entry[]>(`/entries/category/${encodeURIComponent(n)}`),
    add: (entry: NewEntry) => post<{ status: string }>('/entries', entry),
  },
  sum: {
    all: ()              => get<{ hours: number }>('/sum'),
    today: ()            => get<{ hours: number }>('/sum/today'),
    yesterday: ()        => get<{ hours: number }>('/sum/yesterday'),
    byMonth: (m: string) => get<{ hours: number }>(`/sum/month/${m}`),
    byProject: (n: string) => get<{ hours: number }>(`/sum/project/${encodeURIComponent(n)}`),
    byCategory: (n: string) => get<{ hours: number }>(`/sum/category/${encodeURIComponent(n)}`),
    perProject: (m?: string) => get<ProjectSum[]>(`/sum/projects${m ? `?month=${m}` : ''}`),
    perCategory: (m?: string) => get<CategorySum[]>(`/sum/categories${m ? `?month=${m}` : ''}`),
  },
  projects: ()  => get<string[]>('/projects'),
  categories: () => get<string[]>('/categories'),
};
