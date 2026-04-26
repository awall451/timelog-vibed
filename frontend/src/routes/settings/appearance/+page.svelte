<script lang="ts">
  import { settings, THEMES, type Theme } from '$lib/settings.svelte';

  const labels: Record<Theme, string> = {
    default: 'Default',
    tokyonight: 'Tokyo Night',
    cyberpunk: 'Cyberpunk',
    dracula: 'Dracula',
    rosepine: 'Rose Pine',
    catppuccin: 'Catppuccin Latte',
  };
</script>

<h1>Appearance</h1>

<div class="setting-row">
  <div class="setting-info">
    <span class="row-label">Theme</span>
    <p class="hint">
      Pick a color scheme. The quick-switch dropdown in the top-right corner of every
      page reflects the same setting.
    </p>
  </div>
</div>

<div class="theme-grid">
  {#each THEMES as t (t)}
    <button
      class="theme-card"
      class:active={settings.theme === t}
      data-theme-preview={t}
      onclick={() => settings.theme = t}
      type="button"
    >
      <div class="swatches">
        <span class="sw bg"></span>
        <span class="sw surface"></span>
        <span class="sw accent"></span>
        <span class="sw success"></span>
        <span class="sw warning"></span>
      </div>
      <span class="theme-name">{labels[t]}</span>
      {#if settings.theme === t}
        <span class="check" aria-hidden="true">✓</span>
      {/if}
    </button>
  {/each}
</div>

<style>
  h1 {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem;
  }

  .setting-row {
    padding-bottom: 1rem;
  }

  .row-label {
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

  .theme-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 0.8rem;
    margin-top: 0.5rem;
  }

  .theme-card {
    background: var(--surface2);
    border: 2px solid var(--border);
    border-radius: 10px;
    padding: 0.85rem;
    cursor: pointer;
    text-align: left;
    transition: border-color 0.15s, transform 0.15s;
    font-family: inherit;
    color: var(--text);
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
    position: relative;
  }

  .theme-card:hover { border-color: var(--accent-light); }
  .theme-card.active { border-color: var(--accent); }

  .swatches {
    display: flex;
    gap: 0.3rem;
  }

  .sw {
    width: 22px;
    height: 22px;
    border-radius: 5px;
    border: 1px solid rgba(0,0,0,0.15);
  }

  .theme-name {
    font-size: 0.88rem;
    font-weight: 500;
  }

  .check {
    position: absolute;
    top: 0.5rem;
    right: 0.6rem;
    color: var(--accent);
    font-weight: 700;
  }

  /* Per-theme swatch colors. Match the CSS variables defined in +layout.svelte. */
  [data-theme-preview="default"]    .bg { background: #0f1117; }
  [data-theme-preview="default"]    .surface { background: #2d3148; }
  [data-theme-preview="default"]    .accent { background: #6366f1; }
  [data-theme-preview="default"]    .success { background: #22c55e; }
  [data-theme-preview="default"]    .warning { background: #f59e0b; }

  [data-theme-preview="tokyonight"] .bg { background: #1a1b26; }
  [data-theme-preview="tokyonight"] .surface { background: #414868; }
  [data-theme-preview="tokyonight"] .accent { background: #7aa2f7; }
  [data-theme-preview="tokyonight"] .success { background: #9ece6a; }
  [data-theme-preview="tokyonight"] .warning { background: #ff9e64; }

  [data-theme-preview="cyberpunk"]  .bg { background: #0a0a10; }
  [data-theme-preview="cyberpunk"]  .surface { background: #1e1530; }
  [data-theme-preview="cyberpunk"]  .accent { background: #ff2d78; }
  [data-theme-preview="cyberpunk"]  .success { background: #00ffb3; }
  [data-theme-preview="cyberpunk"]  .warning { background: #ffcc00; }

  [data-theme-preview="dracula"]    .bg { background: #282a36; }
  [data-theme-preview="dracula"]    .surface { background: #44475a; }
  [data-theme-preview="dracula"]    .accent { background: #bd93f9; }
  [data-theme-preview="dracula"]    .success { background: #50fa7b; }
  [data-theme-preview="dracula"]    .warning { background: #ffb86c; }

  [data-theme-preview="rosepine"]   .bg { background: #191724; }
  [data-theme-preview="rosepine"]   .surface { background: #26233a; }
  [data-theme-preview="rosepine"]   .accent { background: #c4a7e7; }
  [data-theme-preview="rosepine"]   .success { background: #9ccfd8; }
  [data-theme-preview="rosepine"]   .warning { background: #f6c177; }

  [data-theme-preview="catppuccin"] .bg { background: #eff1f5; }
  [data-theme-preview="catppuccin"] .surface { background: #ccd0da; }
  [data-theme-preview="catppuccin"] .accent { background: #8839ef; }
  [data-theme-preview="catppuccin"] .success { background: #40a02b; }
  [data-theme-preview="catppuccin"] .warning { background: #df8e1d; }
</style>
