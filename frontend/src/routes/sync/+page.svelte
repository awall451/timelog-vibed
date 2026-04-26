<script lang="ts">
  import { api, type ProposedEntry } from '$lib/api';

  const CATEGORIES = ['Development', 'Debugging', 'Planning', 'Documentation', 'Testing', 'Review'];

  interface EditableEntry extends ProposedEntry {
    selected: boolean;
    editingCategory: boolean;
    editingHours: boolean;
    editingDescription: boolean;
  }

  function today(): string {
    return new Date().toISOString().slice(0, 10);
  }

  let date = $state(today());
  let loading = $state(false);
  let error = $state<string | null>(null);
  let entries = $state<EditableEntry[]>([]);
  let analyzed = $state(false);
  let syncing = $state(false);
  let syncResult = $state<{ inserted: number } | null>(null);

  const selectedCount = $derived(entries.filter(e => e.selected).length);
  const hasNew = $derived(entries.some(e => !e.already_exists));

  async function analyze() {
    loading = true;
    error = null;
    analyzed = false;
    syncResult = null;
    entries = [];

    try {
      const result = await api.claude.preview(date);
      entries = result.entries.map(e => ({
        ...e,
        selected: !e.already_exists,
        editingCategory: false,
        editingHours: false,
        editingDescription: false,
      }));
      analyzed = true;
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : String(e);
      error = msg.includes('503')
        ? 'Claude history not found in the container. Add "- ~/.claude:/root/.claude:ro" to api volumes in docker-compose.yml and run tlstart.'
        : `Failed to analyze sessions: ${msg}`;
    } finally {
      loading = false;
    }
  }

  async function syncSelected() {
    const toSync = entries.filter(e => e.selected);
    if (!toSync.length) return;

    syncing = true;
    error = null;
    try {
      const result = await api.claude.sync(
        date,
        toSync.map(e => ({
          project: e.project,
          category: e.category,
          description: e.description,
          hours: e.hours,
        }))
      );
      syncResult = result;
      // mark synced entries as existing
      for (const entry of entries) {
        if (entry.selected) entry.already_exists = true;
      }
    } catch (e: unknown) {
      error = `Sync failed: ${e instanceof Error ? e.message : String(e)}`;
    } finally {
      syncing = false;
    }
  }

  function stopEditing(entry: EditableEntry) {
    entry.editingCategory = false;
    entry.editingHours = false;
    entry.editingDescription = false;
  }
</script>

<div class="page">
  <div class="page-header">
    <h1>AI Sync</h1>
    <p class="subtitle">Generate timelog entries from your Claude Code sessions</p>
  </div>

  <div class="controls">
    <input
      type="date"
      bind:value={date}
      class="date-input"
      onchange={() => { analyzed = false; entries = []; syncResult = null; }}
    />
    <button class="btn-primary" onclick={analyze} disabled={loading}>
      {#if loading}
        <span class="spinner" aria-hidden="true"></span>
        <span>Analyzing…</span>
      {:else}
        Analyze Sessions
      {/if}
    </button>
  </div>

  {#if loading}
    <div class="loading-status" role="status" aria-live="polite">
      <span class="spinner spinner-lg" aria-hidden="true"></span>
      <div class="loading-text">
        <strong>Analyzing Claude sessions for {date}…</strong>
        <span class="loading-hint">Running AI inference on each project — may take 10–30 seconds.</span>
      </div>
    </div>
  {/if}

  {#if error}
    <div class="error-banner">{error}</div>
  {/if}

  {#if syncResult}
    <div class="success-banner">
      Inserted {syncResult.inserted} entr{syncResult.inserted === 1 ? 'y' : 'ies'}.
    </div>
  {/if}

  {#if analyzed && entries.length === 0}
    <div class="empty">No Claude sessions found for {date}.</div>
  {:else if analyzed && !hasNew && !syncResult}
    <div class="empty">All sessions for {date} are already in your timelog.</div>
  {:else if analyzed && entries.length > 0}
    <div class="table-header">
      <span class="table-title">Proposed entries for {date}</span>
      {#if entries.some(e => e.already_exists)}
        <span class="hint">Dimmed rows already exist in your timelog</span>
      {/if}
    </div>

    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th class="col-check"></th>
            <th class="col-project">Project</th>
            <th class="col-category">Category</th>
            <th class="col-hours">Hours</th>
            <th class="col-description">Description</th>
          </tr>
        </thead>
        <tbody>
          {#each entries as entry}
            <tr class:exists={entry.already_exists} class:selected={entry.selected && !entry.already_exists}>
              <td class="col-check">
                <input
                  type="checkbox"
                  bind:checked={entry.selected}
                  disabled={entry.already_exists}
                />
              </td>
              <td class="col-project">
                <span class="project-name">{entry.project}</span>
              </td>

              <!-- Category — click to edit -->
              <td class="col-category" onclick={() => { stopEditing(entry); entry.editingCategory = true; }}>
                {#if entry.editingCategory}
                  <select
                    bind:value={entry.category}
                    onblur={() => entry.editingCategory = false}
                    onchange={() => entry.editingCategory = false}
                    autofocus
                  >
                    {#each CATEGORIES as cat}
                      <option value={cat}>{cat}</option>
                    {/each}
                  </select>
                {:else}
                  <span class="badge editable" title="Click to edit">{entry.category}</span>
                {/if}
              </td>

              <!-- Hours — click to edit -->
              <td class="col-hours" onclick={() => { stopEditing(entry); entry.editingHours = true; }}>
                {#if entry.editingHours}
                  <input
                    type="number"
                    bind:value={entry.hours}
                    step="0.25"
                    min="0.25"
                    max="24"
                    class="hours-input"
                    onblur={() => entry.editingHours = false}
                    autofocus
                  />
                {:else}
                  <span class="hours editable" title="Click to edit">{entry.hours}</span>
                {/if}
              </td>

              <!-- Description — click to edit -->
              <td class="col-description" onclick={() => { stopEditing(entry); entry.editingDescription = true; }}>
                {#if entry.editingDescription}
                  <input
                    type="text"
                    bind:value={entry.description}
                    class="desc-input"
                    onblur={() => entry.editingDescription = false}
                    autofocus
                  />
                {:else}
                  <span class="description editable" title="Click to edit">{entry.description || '—'}</span>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="actions">
      <button
        class="btn-primary"
        onclick={syncSelected}
        disabled={syncing || selectedCount === 0}
      >
        {syncing ? 'Syncing…' : `Sync Selected (${selectedCount})`}
      </button>
    </div>
  {:else if !analyzed && !loading}
    <div class="empty">Pick a date and click <strong>Analyze Sessions</strong> to see your Claude activity.</div>
  {/if}
</div>

<style>
  .page {
    max-width: 960px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
  }

  .page-header {
    margin-bottom: 1.5rem;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--text);
    margin: 0 0 0.25rem;
  }

  .subtitle {
    color: var(--text-muted);
    font-size: 0.875rem;
    margin: 0;
  }

  .controls {
    display: flex;
    gap: 0.75rem;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .date-input {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
    font-family: inherit;
  }

  .btn-primary {
    align-items: center;
    background: var(--accent);
    border: none;
    border-radius: 6px;
    color: #fff;
    cursor: pointer;
    display: inline-flex;
    font-size: 0.875rem;
    font-weight: 600;
    gap: 0.5rem;
    padding: 0.5rem 1.25rem;
    transition: opacity 0.15s;
  }

  .btn-primary:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .spinner {
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: #fff;
    display: inline-block;
    height: 0.875rem;
    width: 0.875rem;
    animation: spin 0.8s linear infinite;
  }

  .spinner-lg {
    border-color: color-mix(in srgb, var(--accent) 25%, transparent);
    border-top-color: var(--accent);
    height: 1.25rem;
    width: 1.25rem;
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .loading-status {
    align-items: center;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    display: flex;
    gap: 0.875rem;
    margin-bottom: 1rem;
    padding: 1rem 1.25rem;
  }

  .loading-text {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
  }

  .loading-text strong {
    color: var(--text);
    font-size: 0.9rem;
    font-weight: 600;
  }

  .loading-hint {
    color: var(--text-muted);
    font-size: 0.8rem;
  }

  .error-banner {
    background: var(--error-bg);
    border: 1px solid var(--error-border);
    border-radius: 6px;
    color: var(--error);
    font-size: 0.875rem;
    margin-bottom: 1rem;
    padding: 0.75rem 1rem;
  }

  .success-banner {
    background: color-mix(in srgb, var(--success) 15%, transparent);
    border: 1px solid color-mix(in srgb, var(--success) 40%, transparent);
    border-radius: 6px;
    color: var(--success);
    font-size: 0.875rem;
    font-weight: 600;
    margin-bottom: 1rem;
    padding: 0.75rem 1rem;
  }

  .empty {
    color: var(--text-muted);
    font-size: 0.9rem;
    padding: 2rem 0;
    text-align: center;
  }

  .table-header {
    align-items: baseline;
    display: flex;
    gap: 1rem;
    margin-bottom: 0.75rem;
  }

  .table-title {
    color: var(--text);
    font-size: 0.875rem;
    font-weight: 600;
  }

  .hint {
    color: var(--text-muted);
    font-size: 0.8rem;
  }

  .table-wrap {
    border: 1px solid var(--border);
    border-radius: 8px;
    overflow: hidden;
  }

  table {
    border-collapse: collapse;
    width: 100%;
  }

  thead {
    background: var(--surface);
  }

  th {
    color: var(--text-muted);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 0.625rem 0.875rem;
    text-align: left;
    text-transform: uppercase;
  }

  td {
    border-top: 1px solid var(--border);
    color: var(--text);
    font-size: 0.875rem;
    padding: 0.625rem 0.875rem;
    vertical-align: middle;
  }

  tr.exists td {
    opacity: 0.4;
  }

  tr.selected td {
    background: color-mix(in srgb, var(--accent) 6%, transparent);
  }

  .col-check { width: 2.5rem; }
  .col-project { width: 14rem; }
  .col-category { width: 11rem; }
  .col-hours { width: 5.5rem; }
  .col-description { /* fills remaining */ }

  .project-name {
    font-weight: 600;
  }

  .badge {
    background: color-mix(in srgb, var(--accent) 18%, transparent);
    border-radius: 4px;
    color: var(--accent);
    display: inline-block;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.5rem;
  }

  .editable {
    cursor: pointer;
  }

  .editable:hover {
    opacity: 0.75;
    text-decoration: underline dotted;
  }

  .hours {
    font-variant-numeric: tabular-nums;
  }

  .description {
    color: var(--text-muted);
  }

  select,
  .hours-input,
  .desc-input {
    background: var(--surface2);
    border: 1px solid var(--accent);
    border-radius: 4px;
    color: var(--text);
    font-family: inherit;
    font-size: 0.875rem;
    outline: none;
    padding: 0.2rem 0.4rem;
  }

  .hours-input {
    width: 5rem;
  }

  .desc-input {
    width: 100%;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1rem;
  }
</style>
