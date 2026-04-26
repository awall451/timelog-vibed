<script lang="ts">
  import { settings } from '$lib/settings.svelte';
</script>

<h1>AI Sync</h1>

<div class="setting-row">
  <div class="setting-info">
    <label for="ai-toggle">Enable AI Sync</label>
    <p class="hint">
      AI Sync reads your local Claude Code session history and suggests timelog entries.
      It is currently a <strong>local-only</strong> feature — the API container needs
      direct access to <code>~/.claude</code> on this machine. When team mode lands later,
      this same toggle will become an org-level feature flag.
    </p>
  </div>
  <div class="setting-control">
    <button
      id="ai-toggle"
      class="toggle"
      class:on={settings.aiSyncEnabled}
      role="switch"
      aria-checked={settings.aiSyncEnabled}
      aria-label="Enable AI Sync"
      onclick={() => settings.aiSyncEnabled = !settings.aiSyncEnabled}
      type="button"
    >
      <span class="knob"></span>
    </button>
  </div>
</div>

<div class="info-box">
  <strong>What changes when this is off?</strong>
  <ul>
    <li>The "AI Sync" link is hidden from the main navigation.</li>
    <li>The <code>/sync</code> page shows a placeholder instead of the analyzer.</li>
    <li>Backend endpoints stay reachable; this is a UI-level toggle only.</li>
  </ul>
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

  .info-box {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.9rem 1rem;
    margin-top: 1.25rem;
    font-size: 0.85rem;
    color: var(--text-secondary);
  }

  .info-box strong {
    color: var(--text);
    display: block;
    margin-bottom: 0.4rem;
  }

  .info-box ul {
    margin: 0;
    padding-left: 1.1rem;
    display: flex;
    flex-direction: column;
    gap: 0.2rem;
  }

  code {
    background: var(--surface);
    padding: 0.05em 0.35em;
    border-radius: 4px;
    font-size: 0.85em;
  }
</style>
