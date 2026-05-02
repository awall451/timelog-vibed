import { existsSync, mkdirSync, copyFileSync, statSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

export default async function globalSetup() {
  const src = resolve(__dirname, '../../../data/timelog.db');
  const dst = resolve(__dirname, '../../static/seed/timelog.db');

  if (!existsSync(src)) {
    throw new Error(
      `globalSetup: seed DB not found at ${src}. ` +
      `Run the main app once (\`tlstart\` + log an entry) so data/timelog.db exists.`
    );
  }
  if (statSync(src).size === 0) {
    throw new Error(`globalSetup: seed DB at ${src} is empty.`);
  }

  mkdirSync(dirname(dst), { recursive: true });
  copyFileSync(src, dst);
  console.log(`[playwright] copied seed DB → ${dst}`);
}
