<script lang="ts">
  import { browser } from '$app/environment';
  import TimerWidget from '$lib/TimerWidget.svelte';
  import SettingsButton from '$lib/SettingsButton.svelte';
  import { settings } from '$lib/settings.svelte';

  let { children } = $props();

  $effect(() => {
    if (browser) {
      document.documentElement.setAttribute('data-theme', settings.theme);
    }
  });
</script>

<svelte:head>
  <title>Timelog</title>
</svelte:head>

<div class="app">
  <header>
    <nav>
      <a href="/" class="brand">🕐 Timelog</a>
      <div class="links">
        <a href="/">Dashboard</a>
        <a href="/entries">Entries</a>
        <a href="/charts">Charts</a>
        {#if !import.meta.env.VITE_DEMO_MODE && settings.aiSyncEnabled}
          <a href="/sync">AI Sync</a>
        {/if}
        <a href="/log">Log Time</a>
      </div>
      <select bind:value={settings.theme} class="theme-select">
        <option value="default">Default</option>
        <option value="tokyonight">Tokyo Night</option>
        <option value="cyberpunk">Cyberpunk</option>
        <option value="dracula">Dracula</option>
        <option value="rosepine">Rose Pine</option>
        <option value="catppuccin">Catppuccin Latte</option>
      </select>
    </nav>
  </header>

  <main>
    {@render children()}
  </main>
</div>

<SettingsButton />
<TimerWidget />

<style>
  :global(:root) {
    --bg: #0f1117;
    --surface: #1a1d27;
    --surface2: #2d3148;
    --border: #2d3148;
    --border-subtle: #1e2235;
    --badge-hover: #3d4268;
    --accent: #6366f1;
    --accent-hover: #4f46e5;
    --accent-light: #a5b4fc;
    --text: #e2e8f0;
    --text-secondary: #cbd5e1;
    --text-muted-mid: #94a3b8;
    --text-muted: #64748b;
    --placeholder: #475569;
    --success: #22c55e;
    --warning: #f59e0b;
    --error: #f87171;
    --error-bg: #2d1a1a;
    --error-border: #7f1d1d;
  }

  :global([data-theme="tokyonight"]) {
    --bg: #1a1b26;
    --surface: #24283b;
    --surface2: #414868;
    --border: #414868;
    --border-subtle: #2a2e42;
    --badge-hover: #545c8a;
    --accent: #7aa2f7;
    --accent-hover: #3d59a1;
    --accent-light: #a9b1d6;
    --text: #c0caf5;
    --text-secondary: #a9b1d6;
    --text-muted-mid: #9aa5ce;
    --text-muted: #565f89;
    --placeholder: #3b4261;
    --success: #9ece6a;
    --warning: #ff9e64;
    --error: #f7768e;
    --error-bg: #2d1b2e;
    --error-border: #6b1830;
  }

  :global([data-theme="cyberpunk"]) {
    --bg: #0a0a10;
    --surface: #12101a;
    --surface2: #1e1530;
    --border: #2a1640;
    --border-subtle: #190e2e;
    --badge-hover: #2e1e48;
    --accent: #ff2d78;
    --accent-hover: #e01060;
    --accent-light: #ff7eb8;
    --text: #f5e8ff;
    --text-secondary: #c8a8f0;
    --text-muted-mid: #7a50a0;
    --text-muted: #4a2870;
    --placeholder: #2e1048;
    --success: #00ffb3;
    --warning: #ffcc00;
    --error: #ff3366;
    --error-bg: #2a0016;
    --error-border: #cc0033;
  }

  :global([data-theme="dracula"]) {
    --bg: #282a36;
    --surface: #21222c;
    --surface2: #44475a;
    --border: #44475a;
    --border-subtle: #343746;
    --badge-hover: #565a73;
    --accent: #bd93f9;
    --accent-hover: #9e6fe6;
    --accent-light: #cfa9ff;
    --text: #f8f8f2;
    --text-secondary: #e0e0d8;
    --text-muted-mid: #a0a8cd;
    --text-muted: #6272a4;
    --placeholder: #4d5577;
    --success: #50fa7b;
    --warning: #ffb86c;
    --error: #ff5555;
    --error-bg: #3a1a1a;
    --error-border: #cc2222;
  }

  :global([data-theme="rosepine"]) {
    --bg: #191724;
    --surface: #1f1d2e;
    --surface2: #26233a;
    --border: #26233a;
    --border-subtle: #211e2f;
    --badge-hover: #2e2a42;
    --accent: #c4a7e7;
    --accent-hover: #a882d4;
    --accent-light: #d8c8f0;
    --text: #e0def4;
    --text-secondary: #c5c0dc;
    --text-muted-mid: #908caa;
    --text-muted: #6e6a86;
    --placeholder: #524f67;
    --success: #9ccfd8;
    --warning: #f6c177;
    --error: #eb6f92;
    --error-bg: #2a1a22;
    --error-border: #8b2040;
  }

  :global([data-theme="catppuccin"]) {
    --bg: #eff1f5;
    --surface: #e6e9ef;
    --surface2: #ccd0da;
    --border: #ccd0da;
    --border-subtle: #dce0e8;
    --badge-hover: #bcc0cc;
    --accent: #8839ef;
    --accent-hover: #7527d7;
    --accent-light: #b09af8;
    --text: #4c4f69;
    --text-secondary: #5c5f77;
    --text-muted-mid: #6c6f85;
    --text-muted: #8c8fa1;
    --placeholder: #9ca0b0;
    --success: #40a02b;
    --warning: #df8e1d;
    --error: #d20f39;
    --error-bg: #f5d5d8;
    --error-border: #e64553;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  :global(html, body) {
    margin: 0;
    background: var(--bg);
  }

  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    color: var(--text);
    min-height: 100vh;
  }

  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  header {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
  }

  nav {
    max-width: 1100px;
    margin: 0 auto;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .brand {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
    text-decoration: none;
    letter-spacing: -0.02em;
  }

  .links {
    display: flex;
    gap: 1.5rem;
  }

  .links a {
    color: var(--text-muted-mid);
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.15s;
  }

  .links a:hover {
    color: var(--text);
  }

  .theme-select {
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text-muted-mid);
    padding: 0.3rem 0.5rem;
    border-radius: 6px;
    font-size: 0.8rem;
    cursor: pointer;
    outline: none;
    transition: border-color 0.15s, color 0.15s;
  }

  .theme-select:focus {
    border-color: var(--accent);
    color: var(--text);
  }

  main {
    flex: 1;
    max-width: 1100px;
    width: 100%;
    margin: 0 auto;
    padding: 2rem;
  }

  @media (max-width: 600px) {
    header { padding: 0 1rem; }

    nav {
      height: auto;
      min-height: 56px;
      flex-wrap: wrap;
      gap: 0.5rem;
      padding: 0.5rem 0;
    }

    .links {
      gap: 0.85rem;
      flex-wrap: wrap;
      order: 3;
      flex-basis: 100%;
    }

    .links a { font-size: 0.85rem; }

    main {
      padding: 1rem;
      padding-bottom: 9rem;
    }
  }
</style>
