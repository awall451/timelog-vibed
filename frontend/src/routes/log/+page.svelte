<script lang="ts">
  import { api } from '$lib/api';
  import { goto } from '$app/navigation';
  import { browser } from '$app/environment';
  import { onMount } from 'svelte';

  let project    = $state('');
  let category   = $state('');
  let description = $state('');
  let hours      = $state('');
  let date       = $state('');
  let submitting = $state(false);
  let error      = $state('');

  const projectSuggestions  = api.projects();
  const categorySuggestions = api.categories();

  onMount(() => {
    if (!browser) return;
    const raw = localStorage.getItem('timer-prefill');
    if (!raw) return;
    try {
      const prefill = JSON.parse(raw);
      if (prefill.project)     project     = prefill.project;
      if (prefill.category)    category    = prefill.category;
      if (prefill.description) description = prefill.description;
      if (prefill.hours)       hours       = String(prefill.hours);
    } catch {}
    localStorage.removeItem('timer-prefill');
  });

  async function submit(e: Event) {
    e.preventDefault();
    error = '';
    const h = parseFloat(hours);
    if (!project || !category || !hours || isNaN(h) || h <= 0) {
      error = 'Project, category, and a positive number of hours are required.';
      return;
    }
    submitting = true;
    try {
      await api.entries.add({ project, category, description, hours: h, date: date || undefined });
      goto('/');
    } catch (err) {
      error = 'Failed to save entry — is tlserve running?';
    } finally {
      submitting = false;
    }
  }
</script>

<div class="page">
  <h1>Log Time</h1>

  <form onsubmit={submit}>
    {#if error}
      <p class="error">{error}</p>
    {/if}

    <div class="field">
      <label for="project">Project</label>
      {#await projectSuggestions then projects}
        <input id="project" list="project-list" bind:value={project} placeholder="e.g. Timelog App" autocomplete="off" />
        <datalist id="project-list">
          {#each projects as p}<option value={p}></option>{/each}
        </datalist>
      {:catch}
        <input id="project" bind:value={project} placeholder="e.g. Timelog App" />
      {/await}
    </div>

    <div class="field">
      <label for="category">Category</label>
      {#await categorySuggestions then categories}
        <input id="category" list="category-list" bind:value={category} placeholder="e.g. Development" autocomplete="off" />
        <datalist id="category-list">
          {#each categories as c}<option value={c}></option>{/each}
        </datalist>
      {:catch}
        <input id="category" bind:value={category} placeholder="e.g. Development" />
      {/await}
    </div>

    <div class="field">
      <label for="description">Description <span class="optional">(optional)</span></label>
      <input id="description" bind:value={description} placeholder="Brief description of work done" />
    </div>

    <div class="row">
      <div class="field">
        <label for="hours">Hours</label>
        <input id="hours" type="number" step="any" min="0.01" bind:value={hours} placeholder="1.5" />
      </div>
      <div class="field">
        <label for="date">Date <span class="optional">(defaults to today)</span></label>
        <input id="date" type="date" bind:value={date} />
      </div>
    </div>

    <div class="actions">
      <a href="/" class="btn-secondary">Cancel</a>
      <button type="submit" class="btn-primary" disabled={submitting}>
        {submitting ? 'Saving…' : 'Save Entry'}
      </button>
    </div>
  </form>
</div>

<style>
  .page {
    max-width: 560px;
  }

  h1 {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    margin-bottom: 2rem;
  }

  form {
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    flex: 1;
  }

  label {
    font-size: 0.82rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-muted-mid);
  }

  .optional {
    text-transform: none;
    letter-spacing: 0;
    font-weight: 400;
    color: var(--text-muted);
  }

  input {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    color: var(--text);
    padding: 0.65rem 0.85rem;
    font-size: 0.95rem;
    width: 100%;
    outline: none;
    transition: border-color 0.15s;
  }

  input:focus {
    border-color: var(--accent);
  }

  input::placeholder {
    color: var(--placeholder);
  }

  .row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  .actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    margin-top: 0.5rem;
  }

  .btn-primary {
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 0.6rem 1.4rem;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s;
  }

  .btn-primary:hover:not(:disabled) { background: var(--accent-hover); }
  .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

  .btn-secondary {
    background: transparent;
    color: var(--text-muted-mid);
    text-decoration: none;
    padding: 0.6rem 1.2rem;
    border-radius: 8px;
    font-size: 0.9rem;
    border: 1px solid var(--border);
    transition: border-color 0.15s;
  }

  .btn-secondary:hover { border-color: var(--text-muted-mid); }

  .error {
    background: var(--error-bg);
    border: 1px solid var(--error-border);
    color: var(--error);
    padding: 0.65rem 0.85rem;
    border-radius: 8px;
    font-size: 0.88rem;
  }
</style>
