#!/usr/bin/env node
import { readdirSync, statSync, copyFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname  = dirname(fileURLToPath(import.meta.url));
const root       = resolve(__dirname, '..');
const resultsDir = join(root, 'test-results');
const destVideo  = join(root, 'static', 'demo.webm');

if (!existsSync(resultsDir)) {
  console.error(`No test-results directory at ${resultsDir}. Run \`npm run record:demo\` first.`);
  process.exit(1);
}

function findVideos(dir) {
  const out = [];
  for (const name of readdirSync(dir)) {
    const full = join(dir, name);
    const st = statSync(full);
    if (st.isDirectory()) {
      out.push(...findVideos(full));
    } else if (name.endsWith('.webm') && full.includes('demo-recording')) {
      out.push({ path: full, mtime: st.mtimeMs });
    }
  }
  return out;
}

const videos = findVideos(resultsDir);
if (!videos.length) {
  console.error('No demo-recording .webm files found in test-results/.');
  process.exit(1);
}

videos.sort((a, b) => b.mtime - a.mtime);
const newest = videos[0];

mkdirSync(dirname(destVideo), { recursive: true });
copyFileSync(newest.path, destVideo);
console.log(`Copied ${newest.path} → ${destVideo}`);
