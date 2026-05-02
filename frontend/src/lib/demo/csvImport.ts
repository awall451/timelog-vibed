import { getDb, persist } from './db';

const REQUIRED = ['id', 'project', 'category', 'description', 'hours', 'date'];

function parseCsv(text: string): Record<string, string>[] {
	const lines = text.replace(/\r\n/g, '\n').split('\n').filter((l) => l.length > 0);
	if (lines.length === 0) return [];
	const headers = splitRow(lines[0]);
	const out: Record<string, string>[] = [];
	for (let i = 1; i < lines.length; i++) {
		const cells = splitRow(lines[i]);
		const row: Record<string, string> = {};
		headers.forEach((h, idx) => (row[h] = cells[idx] ?? ''));
		out.push(row);
	}
	return out;
}

function splitRow(line: string): string[] {
	const out: string[] = [];
	let cur = '';
	let inQuotes = false;
	for (let i = 0; i < line.length; i++) {
		const ch = line[i];
		if (inQuotes) {
			if (ch === '"' && line[i + 1] === '"') {
				cur += '"';
				i++;
			} else if (ch === '"') {
				inQuotes = false;
			} else {
				cur += ch;
			}
		} else {
			if (ch === ',') {
				out.push(cur);
				cur = '';
			} else if (ch === '"') {
				inQuotes = true;
			} else {
				cur += ch;
			}
		}
	}
	out.push(cur);
	return out;
}

export async function importCsv(file: File): Promise<number> {
	const text = await file.text();
	const rows = parseCsv(text);
	if (rows.length === 0) return 0;
	const headerKeys = Object.keys(rows[0]);
	for (const k of REQUIRED) {
		if (!headerKeys.includes(k)) {
			throw new Error(`CSV must have columns: ${REQUIRED.join(', ')}`);
		}
	}
	const db = await getDb();
	db.run('BEGIN');
	try {
		db.run('DELETE FROM entries');
		const stmt = db.prepare(
			'INSERT INTO entries (id, project, category, description, hours, date) VALUES (?, ?, ?, ?, ?, ?)'
		);
		for (const row of rows) {
			stmt.run([
				parseInt(row.id, 10),
				row.project,
				row.category,
				row.description,
				parseFloat(row.hours),
				row.date
			]);
		}
		stmt.free();
		db.run('COMMIT');
	} catch (e) {
		db.run('ROLLBACK');
		throw e;
	}
	await persist();
	return rows.length;
}
