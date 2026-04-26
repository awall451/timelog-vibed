<script lang="ts">
  import { settings, type RoundingMinutes } from '$lib/settings.svelte';

  const ROUNDING_OPTIONS: { value: RoundingMinutes; label: string }[] = [
    { value: 0,  label: 'No rounding (exact)' },
    { value: 5,  label: '5 minutes' },
    { value: 15, label: '15 minutes (default)' },
    { value: 30, label: '30 minutes' },
  ];
</script>

<h1>Timer & Behavior</h1>

<div class="setting-row">
  <div class="setting-info">
    <label for="rounding">Timer rounding on stop</label>
    <p class="hint">
      When you stop the live timer, the elapsed time is rounded to this interval before
      being pre-filled into the log form. "No rounding" passes the exact decimal hours.
    </p>
  </div>
  <div class="setting-control">
    <select id="rounding" bind:value={settings.timerRoundingMinutes}>
      {#each ROUNDING_OPTIONS as opt (opt.value)}
        <option value={opt.value}>{opt.label}</option>
      {/each}
    </select>
  </div>
</div>

<div class="setting-row">
  <div class="setting-info">
    <label for="confirm-delete">Confirm before deleting an entry</label>
    <p class="hint">
      When on, the entries page asks "Delete?" before removing a row. Turn off if you
      prefer one-click deletion.
    </p>
  </div>
  <div class="setting-control">
    <button
      id="confirm-delete"
      class="toggle"
      class:on={settings.confirmDelete}
      role="switch"
      aria-checked={settings.confirmDelete}
      aria-label="Confirm before deleting an entry"
      onclick={() => settings.confirmDelete = !settings.confirmDelete}
      type="button"
    >
      <span class="knob"></span>
    </button>
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

  .setting-control select {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 7px;
    color: var(--text);
    padding: 0.45rem 0.7rem;
    font-size: 0.9rem;
    font-family: inherit;
    outline: none;
    min-width: 12rem;
    transition: border-color 0.15s;
  }

  .setting-control select:focus { border-color: var(--accent); }

  .toggle {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 999px;
    width: 44px;
    height: 24px;
    cursor: pointer;
    position: relative;
    transition: background 0.15s, border-color 0.15s;
    padding: 0;
  }

  .toggle.on {
    background: var(--accent);
    border-color: var(--accent);
  }

  .knob {
    position: absolute;
    top: 2px;
    left: 2px;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--text);
    transition: transform 0.18s ease, background 0.15s;
  }

  .toggle.on .knob {
    transform: translateX(20px);
    background: #fff;
  }
</style>
