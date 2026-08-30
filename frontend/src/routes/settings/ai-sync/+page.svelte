<script lang="ts">
  import { settings } from '$lib/settings.svelte';
</script>

<h1>AI Sync</h1>

{#if import.meta.env.VITE_DEMO_MODE}
  <div class="info-box">
    <strong>Disabled in this demo</strong>
    AI Sync is a <strong>local-only</strong> feature. It reads your Claude Code
    session history from <code>~/.claude</code> on disk, which the in-browser
    demo can't access. Run timelog locally to enable it.
  </div>
{:else}
<div class="setting-row">
  <div class="setting-info">
    <label for="ai-toggle">Enable AI Sync</label>
    <p class="hint">
      AI Sync reads your local AI coding-assistant session history (Claude Code,
      Cursor) and suggests timelog entries. It is currently a <strong>local-only</strong>
      feature — the API container needs direct access to <code>~/.claude</code> and/or
      <code>~/.cursor</code> on this machine. When team mode lands later, this same
      toggle will become an org-level feature flag.
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

<div class="sub-row" class:disabled={!settings.aiSyncEnabled}>
  <div class="setting-info">
    <label for="claude-toggle">Claude Code</label>
    <p class="hint">
      Reads <code>~/.claude/history.jsonl</code> + per-session JSONL. Mount:
      <code>~/.claude:/root/.claude:ro</code>.
    </p>
  </div>
  <div class="setting-control">
    <button
      id="claude-toggle"
      class="toggle"
      class:on={settings.claudeSourceEnabled && settings.aiSyncEnabled}
      role="switch"
      aria-checked={settings.claudeSourceEnabled}
      aria-label="Enable Claude Code source"
      onclick={() => settings.claudeSourceEnabled = !settings.claudeSourceEnabled}
      disabled={!settings.aiSyncEnabled}
      type="button"
    >
      <span class="knob"></span>
    </button>
  </div>
</div>

<div class="sub-row" class:disabled={!settings.aiSyncEnabled}>
  <div class="setting-info">
    <label for="cursor-toggle">Cursor</label>
    <p class="hint">
      Reads <code>~/.cursor/ai-tracking/ai-code-tracking.db</code> (Linux only). Mount:
      <code>~/.cursor:/root/.cursor:ro</code>. Hours from both sources merge as a single
      union of activity intervals — no double-counting.
    </p>
  </div>
  <div class="setting-control">
    <button
      id="cursor-toggle"
      class="toggle"
      class:on={settings.cursorSourceEnabled && settings.aiSyncEnabled}
      role="switch"
      aria-checked={settings.cursorSourceEnabled}
      aria-label="Enable Cursor source"
      onclick={() => settings.cursorSourceEnabled = !settings.cursorSourceEnabled}
      disabled={!settings.aiSyncEnabled}
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
{/if}

<style>
  h1 {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 1.5rem;
  }

  .setting-row,
  .sub-row {
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 2rem;
    padding: 1.25rem 0;
    border-bottom: 1px solid var(--border-subtle);
    align-items: start;
  }

  .sub-row {
    padding-left: 1.5rem;
  }

  .sub-row.disabled {
    opacity: 0.45;
  }

  .toggle:disabled {
    cursor: not-allowed;
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
