<script lang="ts">
  import { page } from '$app/state';

  let onSettings = $derived(page.url.pathname.startsWith('/settings'));
</script>

<a
  class="settings-btn"
  class:active={onSettings}
  href="/settings"
  title="Settings"
  aria-label="Settings"
>
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h.1a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v.1a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
  </svg>
</a>

<style>
  .settings-btn {
    position: fixed;
    bottom: 1.5rem;
    left: 1.5rem;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--surface);
    border: 2px solid var(--border);
    color: var(--text-muted);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: border-color 0.15s, color 0.15s, transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    z-index: 1000;
    text-decoration: none;
  }

  .settings-btn:hover {
    border-color: var(--accent);
    color: var(--accent);
    transform: rotate(45deg);
  }

  .settings-btn.active {
    border-color: var(--accent);
    color: var(--accent);
  }

  .settings-btn svg {
    width: 22px;
    height: 22px;
    fill: none;
    stroke: currentColor;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
</style>
