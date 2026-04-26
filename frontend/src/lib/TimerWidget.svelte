<script lang="ts">
  import { browser } from '$app/environment';
  import { goto } from '$app/navigation';
  import { api } from '$lib/api';
  import { settings } from '$lib/settings.svelte';

  type TimerStatus = 'idle' | 'running';

  interface TimerState {
    status: TimerStatus;
    startedAt: number | null;
    project: string;
    category: string;
    description: string;
  }

  const STORAGE_KEY = 'timer-state';
  const PREFILL_KEY = 'timer-prefill';

  function defaultState(): TimerState {
    return { status: 'idle', startedAt: null, project: '', category: '', description: '' };
  }

  function loadState(): TimerState {
    if (!browser) return defaultState();
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch {}
    return defaultState();
  }

  let expanded = $state(false);
  let timerState = $state<TimerState>(loadState());
  let elapsed = $state(0);
  let clockNow = $state(Date.now());

  const projectSuggestions = browser ? api.projects() : Promise.resolve([]);
  const categorySuggestions = browser ? api.categories() : Promise.resolve([]);

  $effect(() => {
    if (browser) localStorage.setItem(STORAGE_KEY, JSON.stringify(timerState));
  });

  $effect(() => {
    if (timerState.status === 'running' && timerState.startedAt) {
      elapsed = Math.floor((Date.now() - timerState.startedAt) / 1000);
    }
    const id = setInterval(() => {
      clockNow = Date.now();
      if (timerState.status === 'running' && timerState.startedAt) {
        elapsed = Math.floor((Date.now() - timerState.startedAt) / 1000);
      }
    }, 1000);
    return () => clearInterval(id);
  });

  let clockAngles = $derived.by(() => {
    const d = new Date(clockNow);
    const s = d.getSeconds();
    const m = d.getMinutes() + s / 60;
    const h = (d.getHours() % 12) + m / 60;
    return {
      second: s * 6,
      minute: m * 6,
      hour: h * 30,
    };
  });

  function formatElapsed(secs: number): string {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  function start() {
    if (!timerState.project || !timerState.category) return;
    timerState = { ...timerState, status: 'running', startedAt: Date.now() };
  }

  function roundHours(rawHours: number, mins: number): number {
    if (mins === 0) return Math.max(0.01, Math.round(rawHours * 1000) / 1000);
    const fraction = mins / 60;
    return Math.max(fraction, Math.round(rawHours / fraction) * fraction);
  }

  function stop() {
    if (!timerState.startedAt) return;
    const rawHours = (Date.now() - timerState.startedAt) / 3600000;
    const hours = roundHours(rawHours, settings.timerRoundingMinutes);
    if (browser) {
      localStorage.setItem(PREFILL_KEY, JSON.stringify({
        project: timerState.project,
        category: timerState.category,
        description: timerState.description,
        hours,
      }));
    }
    timerState = defaultState();
    elapsed = 0;
    expanded = false;
    goto('/log');
  }
</script>

<div class="widget">
  {#if expanded}
    <div class="panel">
      {#if timerState.status === 'running'}
        <div class="elapsed">{formatElapsed(elapsed)}</div>
        <div class="running-info">
          <span>{timerState.project}</span>
          <span class="sep">·</span>
          <span>{timerState.category}</span>
        </div>
        <button class="stop-btn" onclick={stop}>Stop & Log</button>
      {:else}
        {#await projectSuggestions then projects}
          <input list="tw-projects" bind:value={timerState.project} placeholder="Project" autocomplete="off" />
          <datalist id="tw-projects">
            {#each projects as p}<option value={p}></option>{/each}
          </datalist>
        {:catch}
          <input bind:value={timerState.project} placeholder="Project" />
        {/await}

        {#await categorySuggestions then categories}
          <input list="tw-categories" bind:value={timerState.category} placeholder="Category" autocomplete="off" />
          <datalist id="tw-categories">
            {#each categories as c}<option value={c}></option>{/each}
          </datalist>
        {:catch}
          <input bind:value={timerState.category} placeholder="Category" />
        {/await}

        <input bind:value={timerState.description} placeholder="Description (optional)" />

        <button class="start-btn" onclick={start} disabled={!timerState.project || !timerState.category}>
          Start Timer
        </button>
      {/if}
    </div>
  {/if}

  <!-- sprite-btn: replace SVG content below with custom artwork when ready -->
  <button
    class="sprite-btn"
    class:running={timerState.status === 'running'}
    onclick={() => expanded = !expanded}
    title={timerState.status === 'running' ? formatElapsed(elapsed) : 'Start timer'}
    aria-label="Timer"
  >
    {#if timerState.status === 'running'}
      <div class="pulse"></div>
    {/if}
    <svg class="clock" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
      <circle class="face" cx="32" cy="32" r="28" />
      <circle class="face-ring" cx="32" cy="32" r="28" />
      {#each Array(12) as _, i}
        <line
          class="tick"
          x1="32" y1="8"
          x2="32" y2={i % 3 === 0 ? 14 : 11}
          transform={`rotate(${i * 30} 32 32)`}
        />
      {/each}
      <line
        class="hand hour-hand"
        x1="32" y1="32" x2="32" y2="17"
        transform={`rotate(${clockAngles.hour} 32 32)`}
      />
      <line
        class="hand minute-hand"
        x1="32" y1="32" x2="32" y2="10"
        transform={`rotate(${clockAngles.minute} 32 32)`}
      />
      <line
        class="hand second-hand"
        x1="32" y1="36" x2="32" y2="8"
        transform={`rotate(${clockAngles.second} 32 32)`}
      />
      <circle class="center-dot" cx="32" cy="32" r="2.5" />
    </svg>
  </button>
</div>

<style>
  .widget {
    position: fixed;
    bottom: 1.5rem;
    right: 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.75rem;
    z-index: 1000;
    max-height: calc(100vh - 2rem);
  }

  .panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    width: min(260px, calc(100vw - 3rem));
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
  }

  .panel input {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    padding: 0.5rem 0.7rem;
    font-size: 0.88rem;
    outline: none;
    transition: border-color 0.15s;
    font-family: inherit;
  }

  .panel input:focus { border-color: var(--accent); }
  .panel input::placeholder { color: var(--text-muted-mid); }

  .start-btn {
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.5rem;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s;
    margin-top: 0.2rem;
    font-family: inherit;
    align-self: stretch;
  }

  .start-btn:hover:not(:disabled) { background: var(--accent-hover); }
  .start-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .stop-btn {
    background: var(--error);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 0.5rem;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    font-family: inherit;
    transition: opacity 0.15s;
    align-self: stretch;
  }

  .stop-btn:hover { opacity: 0.85; }

  .elapsed {
    font-size: 1.6rem;
    font-weight: 700;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.02em;
    color: var(--text);
    text-align: center;
  }

  .running-info {
    display: flex;
    gap: 0.4rem;
    justify-content: center;
    font-size: 0.8rem;
    color: var(--text-muted-mid);
  }

  .sep { color: var(--text-muted); }

  .sprite-btn {
    position: relative;
    background: var(--surface);
    border: 2px solid var(--border);
    border-radius: 50%;
    width: 112px;
    height: 112px;
    cursor: pointer;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: border-color 0.15s, box-shadow 0.15s;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
  }

  .sprite-btn:hover { border-color: var(--accent); }
  .sprite-btn.running { border-color: var(--accent); }

  .pulse {
    position: absolute;
    inset: -5px;
    border-radius: 50%;
    border: 2px solid var(--accent);
    animation: pulse 2s ease-out infinite;
    pointer-events: none;
  }

  @keyframes pulse {
    0%   { opacity: 0.8; transform: scale(1); }
    100% { opacity: 0;   transform: scale(1.5); }
  }

  .clock {
    width: 100px;
    height: 100px;
  }

  .face      { fill: var(--surface2); }
  .face-ring { fill: none; stroke: var(--border); stroke-width: 2; }

  .tick {
    stroke: var(--text-muted);
    stroke-width: 1.5;
    stroke-linecap: round;
  }

  .hand {
    stroke-linecap: round;
  }

  .hour-hand   { stroke: var(--text); stroke-width: 3; }
  .minute-hand { stroke: var(--text); stroke-width: 2; }
  .second-hand { stroke: var(--accent); stroke-width: 1.5; }

  .center-dot { fill: var(--accent); }
</style>
