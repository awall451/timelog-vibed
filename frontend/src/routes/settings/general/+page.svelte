<script lang="ts">
  import { settings, setSetting } from '$lib/settings.svelte';

  let goalInput = $state(String(settings.dailyGoalHours));
  let goalError = $state('');

  function commitGoal() {
    const n = parseFloat(goalInput);
    if (isNaN(n) || n <= 0 || n > 24) {
      goalError = 'Enter a number between 0.5 and 24.';
      goalInput = String(settings.dailyGoalHours);
      return;
    }
    goalError = '';
    setSetting('dailyGoalHours', n);
  }
</script>

<h1>General</h1>

<div class="setting-row">
  <div class="setting-info">
    <label for="goal">Daily hours goal</label>
    <p class="hint">
      Used everywhere the app shows progress toward a daily target — the dashboard stat,
      the heatmap intensity scale, and the goal line on the charts pace plot.
    </p>
  </div>
  <div class="setting-control">
    <input
      id="goal"
      type="number"
      step="0.25"
      min="0.5"
      max="24"
      bind:value={goalInput}
      onblur={commitGoal}
      onkeydown={(e) => { if (e.key === 'Enter') (e.currentTarget as HTMLInputElement).blur(); }}
    />
    <span class="unit">hours</span>
    {#if goalError}<p class="error">{goalError}</p>{/if}
  </div>
</div>

<div class="setting-row">
  <div class="setting-info">
    <label for="weekstart">Week starts on</label>
    <p class="hint">Affects the row alignment of the activity heatmap on the Entries page.</p>
  </div>
  <div class="setting-control">
    <select id="weekstart" bind:value={settings.weekStart}>
      <option value="sun">Sunday</option>
      <option value="mon">Monday</option>
    </select>
  </div>
</div>

<style>
  h1 {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem;
  }

  .setting-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 2rem;
    padding: 1.25rem 0;
    border-bottom: 1px solid var(--border-subtle);
    align-items: start;
  }

  .setting-row:last-of-type { border-bottom: none; }

  .setting-info label {
    display: block;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text);
    margin-bottom: 0.3rem;
  }

  .hint {
    font-size: 0.83rem;
    color: var(--text-muted);
    line-height: 1.5;
    max-width: 42rem;
  }

  .setting-control {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 0.4rem;
  }

  .setting-control input,
  .setting-control select {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 7px;
    color: var(--text);
    padding: 0.45rem 0.7rem;
    font-size: 0.9rem;
    font-family: inherit;
    outline: none;
    min-width: 7rem;
    transition: border-color 0.15s;
  }

  .setting-control input:focus,
  .setting-control select:focus {
    border-color: var(--accent);
  }

  .unit {
    font-size: 0.78rem;
    color: var(--text-muted);
  }

  .error {
    font-size: 0.78rem;
    color: var(--error);
  }
</style>
