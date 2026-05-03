const BASE = import.meta.env.VITE_API_BASE ?? 'http://localhost:8888';

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

export interface ProposedEntry {
  project: string;
  category: string;
  description: string;
  hours: number;
  already_exists: boolean;
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

async function put<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

async function del(path: string): Promise<void> {
  const res = await fetch(`${BASE}${path}`, { method: 'DELETE' });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
}

const realApi = {
  entries: {
    all: ()              => get<Entry[]>('/entries'),
    today: ()            => get<Entry[]>('/entries/today'),
    yesterday: ()        => get<Entry[]>('/entries/yesterday'),
    last: ()             => get<Entry>('/entries/last'),
    byMonth: (m: string) => get<Entry[]>(`/entries/month/${m}`),
    byProject: (n: string) => get<Entry[]>(`/entries/project/${encodeURIComponent(n)}`),
    byCategory: (n: string) => get<Entry[]>(`/entries/category/${encodeURIComponent(n)}`),
    add: (entry: NewEntry) => post<{ status: string }>('/entries', entry),
    update: (id: number, entry: NewEntry) => put<Entry>(`/entries/${id}`, entry),
    delete: (id: number) => del(`/entries/${id}`),
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
  claude: {
    preview: (date: string) =>
      get<{ date: string; entries: ProposedEntry[] }>(`/claude/preview?date=${date}`),
    sync: (date: string, entries: NewEntry[]) =>
      post<{ inserted: number }>('/claude/sync', { date, entries }),
  },
};

// Avoid top-level await so older Safari (iOS < 15) parses this module.
// In demo mode we resolve the demo api lazily; in main mode we wrap a
// resolved promise around realApi so the call shape stays uniform. The
// dynamic import is still gated on VITE_DEMO_MODE so the demo bundle
// (sql.js + WASM) stays out of the main app chunk.
const apiPromise: Promise<typeof realApi> = import.meta.env.VITE_DEMO_MODE
  ? import('./demo/api').then((m) => m.api as typeof realApi)
  : Promise.resolve(realApi);

function lazy<T extends (...args: any[]) => any>(path: readonly string[]): T {
  return (async (...args: any[]) => {
    const root: any = await apiPromise;
    let target: any = root;
    let owner: any = root;
    for (const p of path) {
      owner = target;
      target = target[p];
    }
    return target.apply(owner, args);
  }) as T;
}

export const api: typeof realApi = {
  entries: {
    all:        lazy(['entries', 'all']),
    today:      lazy(['entries', 'today']),
    yesterday:  lazy(['entries', 'yesterday']),
    last:       lazy(['entries', 'last']),
    byMonth:    lazy(['entries', 'byMonth']),
    byProject:  lazy(['entries', 'byProject']),
    byCategory: lazy(['entries', 'byCategory']),
    add:        lazy(['entries', 'add']),
    update:     lazy(['entries', 'update']),
    delete:     lazy(['entries', 'delete']),
  },
  sum: {
    all:         lazy(['sum', 'all']),
    today:       lazy(['sum', 'today']),
    yesterday:   lazy(['sum', 'yesterday']),
    byMonth:     lazy(['sum', 'byMonth']),
    byProject:   lazy(['sum', 'byProject']),
    byCategory:  lazy(['sum', 'byCategory']),
    perProject:  lazy(['sum', 'perProject']),
    perCategory: lazy(['sum', 'perCategory']),
  },
  projects:   lazy(['projects']),
  categories: lazy(['categories']),
  claude: {
    preview: lazy(['claude', 'preview']),
    sync:    lazy(['claude', 'sync']),
  },
};
