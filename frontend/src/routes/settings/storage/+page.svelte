<script lang="ts">
  import { resetSettings } from '$lib/settings.svelte';

  let confirming = $state(false);
  let resetDone  = $state(false);

  function doReset() {
    resetSettings();
    confirming = false;
    resetDone = true;
    setTimeout(() => resetDone = false, 2500);
  }
</script>

<h1>Data</h1>

<div class="setting-row">
  <div class="setting-info">
    <span class="row-label">Reset all settings</span>
    <p class="hint">
      Restores every preference on this page back to its default value. Your timelog
      entries are <strong>not</strong> affected — only this page's settings.
    </p>
  </div>
  <div class="setting-control">
    {#if resetDone}
      <span class="ok">Done.</span>
    {:else if !confirming}
      <button class="btn-danger" onclick={() => confirming = true} type="button">
        Reset to defaults
      </button>
    {:else}
      <div class="confirm">
        <span>Are you sure?</span>
        <button class="btn-danger" onclick={doReset} type="button">Yes, reset</button>
        <button class="btn-cancel" onclick={() => confirming = false} type="button">Cancel</button>
      </div>
    {/if}
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
    align-items: start;
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

  .btn-danger {
    background: var(--error);
    color: #fff;
    border: none;
    border-radius: 7px;
    padding: 0.5rem 1rem;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    font-family: inherit;
    transition: opacity 0.15s;
  }

  .btn-danger:hover { opacity: 0.85; }

  .btn-cancel {
    background: transparent;
    color: var(--text-muted-mid);
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 0.5rem 1rem;
    font-size: 0.88rem;
    cursor: pointer;
    font-family: inherit;
    transition: border-color 0.15s;
  }

  .btn-cancel:hover { border-color: var(--text-muted-mid); }

  .confirm {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: var(--text-muted-mid);
  }

  .ok {
    color: var(--success);
    font-size: 0.88rem;
    font-weight: 500;
  }
</style>
