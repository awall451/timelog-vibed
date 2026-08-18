import initSqlJs, { type Database, type SqlJsStatic } from 'sql.js';
import sqlWasmUrl from 'sql.js/dist/sql-wasm.wasm?url';
import { get, set, del } from 'idb-keyval';
import { base } from '$app/paths';

const STORAGE_KEY = 'timelog-demo-db-v1';

let SQL: SqlJsStatic | null = null;
let dbInstance: Database | null = null;
let initPromise: Promise<Database> | null = null;

async function load(): Promise<Database> {
	if (!SQL) {
		SQL = await initSqlJs({ locateFile: () => sqlWasmUrl });
	}
	const stored = await get<Uint8Array>(STORAGE_KEY);
	if (stored) {
		return new SQL.Database(stored);
	}
	const res = await fetch(`${base}/seed/timelog.db`);
	if (!res.ok) throw new Error(`Failed to load seed DB: ${res.status}`);
	const bytes = new Uint8Array(await res.arrayBuffer());
	return new SQL.Database(bytes);
}

/** Today's date as YYYY-MM-DD in the visitor's local timezone. */
function localToday(): string {
	return new Date().toLocaleDateString('sv-SE');
}

/**
 * Calendar-anchored date rotation. Every row keeps its month-day but gets its
 * year recomputed so it falls in the trailing 365-day window ending today:
 *   year = (MM-DD <= today's MM-DD) ? thisYear : thisYear - 1
 * Idempotent and stateless, so it runs on every load (fresh seed and
 * IndexedDB-hydrated copies alike). Rows dated 02-29 are left untouched —
 * they would be invalid in a non-leap year.
 * Returns the number of rows that actually changed.
 */
export function reyear(db: Database, today: string = localToday()): number {
	const y = Number(today.slice(0, 4));
	const mmdd = today.slice(5);
	db.run(
		`UPDATE entries
		    SET date = CASE WHEN substr(date, 6) <= ? THEN ? || substr(date, 5)
		                    ELSE ? || substr(date, 5) END
		  WHERE substr(date, 6) <> '02-29'
		    AND date <> CASE WHEN substr(date, 6) <= ? THEN ? || substr(date, 5)
		                     ELSE ? || substr(date, 5) END`,
		[mmdd, String(y), String(y - 1), mmdd, String(y), String(y - 1)]
	);
	return db.getRowsModified();
}

export async function getDb(): Promise<Database> {
	if (dbInstance) return dbInstance;
	if (!initPromise) {
		initPromise = load().then(async (db) => {
			dbInstance = db;
			if (reyear(db) > 0) await persist();
			return db;
		});
	}
	return initPromise;
}

export async function persist(): Promise<void> {
	if (!dbInstance) return;
	await set(STORAGE_KEY, dbInstance.export());
}

export async function reset(): Promise<void> {
	if (dbInstance) {
		dbInstance.close();
		dbInstance = null;
	}
	initPromise = null;
	await del(STORAGE_KEY);
}
