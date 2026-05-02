import type { Database } from 'sql.js';
import { getDb, persist } from './db';
import type { Entry, NewEntry, ProjectSum, CategorySum, ProposedEntry } from '../api';

export type { Entry, NewEntry, ProjectSum, CategorySum, ProposedEntry };

function rows<T>(db: Database, sql: string, params: (string | number | null)[] = []): T[] {
	const stmt = db.prepare(sql);
	stmt.bind(params);
	const out: T[] = [];
	while (stmt.step()) out.push(stmt.getAsObject() as T);
	stmt.free();
	return out;
}

function one<T>(db: Database, sql: string, params: (string | number | null)[] = []): T | null {
	const r = rows<T>(db, sql, params);
	return r.length > 0 ? r[0] : null;
}

function localDate(offsetDays = 0): string {
	const d = new Date();
	d.setDate(d.getDate() + offsetDays);
	return d.toLocaleDateString('sv-SE');
}

function sumValue(db: Database, sql: string, params: (string | number | null)[] = []): number {
	const r = one<Record<string, number>>(db, sql, params);
	if (!r) return 0;
	const key = Object.keys(r)[0];
	return r[key] ?? 0;
}

export const api = {
	entries: {
		all: async (): Promise<Entry[]> => {
			const db = await getDb();
			return rows<Entry>(db, 'SELECT * FROM entries ORDER BY date, id');
		},
		today: async (): Promise<Entry[]> => {
			const db = await getDb();
			return rows<Entry>(db, 'SELECT * FROM entries WHERE date = ? ORDER BY id', [localDate()]);
		},
		yesterday: async (): Promise<Entry[]> => {
			const db = await getDb();
			return rows<Entry>(db, 'SELECT * FROM entries WHERE date = ? ORDER BY id', [localDate(-1)]);
		},
		last: async (): Promise<Entry> => {
			const db = await getDb();
			const r = one<Entry>(db, 'SELECT * FROM entries ORDER BY id DESC LIMIT 1');
			if (!r) throw new Error('API error: 404');
			return r;
		},
		byMonth: async (m: string): Promise<Entry[]> => {
			const db = await getDb();
			return rows<Entry>(
				db,
				"SELECT * FROM entries WHERE strftime('%Y-%m', date) = ? ORDER BY date, id",
				[m]
			);
		},
		byProject: async (n: string): Promise<Entry[]> => {
			const db = await getDb();
			return rows<Entry>(db, 'SELECT * FROM entries WHERE project = ? ORDER BY date, id', [n]);
		},
		byCategory: async (n: string): Promise<Entry[]> => {
			const db = await getDb();
			return rows<Entry>(db, 'SELECT * FROM entries WHERE category = ? ORDER BY date, id', [n]);
		},
		add: async (entry: NewEntry): Promise<{ status: string }> => {
			const db = await getDb();
			const date = entry.date ?? localDate();
			db.run(
				'INSERT INTO entries (project, category, description, hours, date) VALUES (?, ?, ?, ?, ?)',
				[entry.project, entry.category, entry.description ?? '', entry.hours, date]
			);
			await persist();
			return { status: 'added' };
		},
		update: async (id: number, entry: NewEntry): Promise<Entry> => {
			const db = await getDb();
			db.run(
				'UPDATE entries SET project=?, category=?, description=?, hours=?, date=? WHERE id=?',
				[
					entry.project,
					entry.category,
					entry.description ?? '',
					entry.hours,
					entry.date ?? localDate(),
					id
				]
			);
			const r = one<Entry>(db, 'SELECT * FROM entries WHERE id=?', [id]);
			await persist();
			if (!r) throw new Error('API error: 404');
			return r;
		},
		delete: async (id: number): Promise<void> => {
			const db = await getDb();
			db.run('DELETE FROM entries WHERE id = ?', [id]);
			await persist();
		}
	},
	sum: {
		all: async () => {
			const db = await getDb();
			return { hours: sumValue(db, 'SELECT COALESCE(SUM(hours), 0) AS h FROM entries') };
		},
		today: async () => {
			const db = await getDb();
			return {
				hours: sumValue(db, 'SELECT COALESCE(SUM(hours), 0) AS h FROM entries WHERE date = ?', [
					localDate()
				])
			};
		},
		yesterday: async () => {
			const db = await getDb();
			return {
				hours: sumValue(db, 'SELECT COALESCE(SUM(hours), 0) AS h FROM entries WHERE date = ?', [
					localDate(-1)
				])
			};
		},
		byMonth: async (m: string) => {
			const db = await getDb();
			return {
				hours: sumValue(
					db,
					"SELECT COALESCE(SUM(hours), 0) AS h FROM entries WHERE strftime('%Y-%m', date) = ?",
					[m]
				)
			};
		},
		byProject: async (n: string) => {
			const db = await getDb();
			return {
				hours: sumValue(
					db,
					'SELECT COALESCE(SUM(hours), 0) AS h FROM entries WHERE project = ?',
					[n]
				)
			};
		},
		byCategory: async (n: string) => {
			const db = await getDb();
			return {
				hours: sumValue(
					db,
					'SELECT COALESCE(SUM(hours), 0) AS h FROM entries WHERE category = ?',
					[n]
				)
			};
		},
		perProject: async (m?: string): Promise<ProjectSum[]> => {
			const db = await getDb();
			if (m) {
				return rows<ProjectSum>(
					db,
					"SELECT project, SUM(hours) AS hours FROM entries WHERE strftime('%Y-%m', date) = ? GROUP BY project ORDER BY hours DESC",
					[m]
				);
			}
			return rows<ProjectSum>(
				db,
				'SELECT project, SUM(hours) AS hours FROM entries GROUP BY project ORDER BY hours DESC'
			);
		},
		perCategory: async (m?: string): Promise<CategorySum[]> => {
			const db = await getDb();
			if (m) {
				return rows<CategorySum>(
					db,
					"SELECT category, SUM(hours) AS hours FROM entries WHERE strftime('%Y-%m', date) = ? GROUP BY category ORDER BY hours DESC",
					[m]
				);
			}
			return rows<CategorySum>(
				db,
				'SELECT category, SUM(hours) AS hours FROM entries GROUP BY category ORDER BY hours DESC'
			);
		}
	},
	projects: async (): Promise<string[]> => {
		const db = await getDb();
		return rows<{ project: string }>(
			db,
			'SELECT DISTINCT project FROM entries ORDER BY project'
		).map((r) => r.project);
	},
	categories: async (): Promise<string[]> => {
		const db = await getDb();
		return rows<{ category: string }>(
			db,
			'SELECT DISTINCT category FROM entries ORDER BY category'
		).map((r) => r.category);
	},
	claude: {
		preview: async (_date: string): Promise<{ date: string; entries: ProposedEntry[] }> => {
			throw new Error('AI Sync is a local-only feature. Run timelog locally to enable.');
		},
		sync: async (_date: string, _entries: NewEntry[]): Promise<{ inserted: number }> => {
			throw new Error('AI Sync is a local-only feature. Run timelog locally to enable.');
		}
	}
};
