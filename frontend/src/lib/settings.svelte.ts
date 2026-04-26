import { browser } from '$app/environment';

export const THEMES = ['default', 'tokyonight', 'cyberpunk', 'dracula', 'rosepine', 'catppuccin'] as const;
export type Theme = typeof THEMES[number];

export type WeekStart = 'sun' | 'mon';
export type RoundingMinutes = 0 | 5 | 15 | 30;

export interface Settings {
  version: 1;
  theme: Theme;
  dailyGoalHours: number;
  aiSyncEnabled: boolean;
  weekStart: WeekStart;
  timerRoundingMinutes: RoundingMinutes;
  confirmDelete: boolean;
}

export const DEFAULT_SETTINGS: Settings = {
  version: 1,
  theme: 'default',
  dailyGoalHours: 8,
  aiSyncEnabled: true,
  weekStart: 'sun',
  timerRoundingMinutes: 15,
  confirmDelete: true,
};

const STORAGE_KEY = 'timelog-settings';
const LEGACY_THEME_KEY = 'theme';

function isTheme(v: unknown): v is Theme {
  return typeof v === 'string' && (THEMES as readonly string[]).includes(v);
}

function sanitize(raw: unknown): Settings {
  const out: Settings = { ...DEFAULT_SETTINGS };
  if (!raw || typeof raw !== 'object') return out;
  const r = raw as Record<string, unknown>;
  if (isTheme(r.theme)) out.theme = r.theme;
  if (typeof r.dailyGoalHours === 'number' && r.dailyGoalHours > 0 && r.dailyGoalHours <= 24) {
    out.dailyGoalHours = r.dailyGoalHours;
  }
  if (typeof r.aiSyncEnabled === 'boolean') out.aiSyncEnabled = r.aiSyncEnabled;
  if (r.weekStart === 'sun' || r.weekStart === 'mon') out.weekStart = r.weekStart;
  if (r.timerRoundingMinutes === 0 || r.timerRoundingMinutes === 5 || r.timerRoundingMinutes === 15 || r.timerRoundingMinutes === 30) {
    out.timerRoundingMinutes = r.timerRoundingMinutes;
  }
  if (typeof r.confirmDelete === 'boolean') out.confirmDelete = r.confirmDelete;
  return out;
}

function load(): Settings {
  if (!browser) return { ...DEFAULT_SETTINGS };
  let parsed: unknown = null;
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) parsed = JSON.parse(raw);
  } catch {}
  const result = sanitize(parsed);

  // Legacy migration: prior versions stored theme under 'theme'.
  if (!parsed) {
    const legacy = localStorage.getItem(LEGACY_THEME_KEY);
    if (isTheme(legacy)) result.theme = legacy;
  }
  if (localStorage.getItem(LEGACY_THEME_KEY) !== null) {
    localStorage.removeItem(LEGACY_THEME_KEY);
  }
  return result;
}

function save(s: Settings): void {
  if (!browser) return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
}

export const settings = $state<Settings>(load());

if (browser) {
  $effect.root(() => {
    $effect(() => save({ ...settings }));
  });
}

export function setSetting<K extends keyof Settings>(key: K, value: Settings[K]): void {
  settings[key] = value;
}

export function resetSettings(): void {
  Object.assign(settings, DEFAULT_SETTINGS);
}
