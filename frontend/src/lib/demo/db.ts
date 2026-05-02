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

export async function getDb(): Promise<Database> {
	if (dbInstance) return dbInstance;
	if (!initPromise) {
		initPromise = load().then((db) => {
			dbInstance = db;
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
