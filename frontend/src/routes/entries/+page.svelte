<script lang="ts">
  import { api, type Entry } from '$lib/api';

  let allEntries  = $state<Entry[]>([]);
  let loading     = $state(true);
  let loadError   = $state(false);

  let dateFilter  = $state('all');
  let month       = $state('');
  let project     = $state('');
  let category    = $state('');

  const projects   = api.projects();
  const categories = api.categories();

  const today     = new Date().toISOString().split('T')[0];
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

  api.entries.all()
    .then(e  => { allEntries = e; loading = false; })
    .catch(() => { loadError = true; loading = false; });

  let filtered = $derived(allEntries.filter(e => {
    if (dateFilter === 'today'     && e.date !== today)                return false;
    if (dateFilter === 'yesterday' && e.date !== yesterday)            return false;
    if (dateFilter === 'month'     && month && !e.date.startsWith(month)) return false;
    if (project  && e.project  !== project)                            return false;
    if (category && e.category !== category)                           return false;
    return true;
  }));

  let totalHours = $derived(filtered.reduce((s, e) => s + e.hours, 0));
</script>

<div class="page">
  <div class="page-header">
    <h1>Entries</h1>
    <a href="/log" class="btn-primary">+ Log Time</a>
  </div>

  <div class="filters">
    <div class="filter-row">
      <button class:active={dateFilter === 'all'}       onclick={() => dateFilter = 'all'}>All</button>
      <button class:active={dateFilter === 'today'}     onclick={() => dateFilter = 'today'}>Today</button>
      <button class:active={dateFilter === 'yesterday'} onclick={() => dateFilter = 'yesterday'}>Yesterday</button>
      <button class:active={dateFilter === 'month'}     onclick={() => dateFilter = 'month'}>Date</button>
      {#if dateFilter === 'month'}
        <input type="month" bind:value={month} />
      {/if}
    </div>

    <div class="filter-row">
      {#await projects then list}
        <select bind:value={project}>
          <option value="">All projects</option>
          {#each list as p}<option value={p}>{p}</option>{/each}
        </select>
      {/await}

      {#await categories then list}
        <select bind:value={category}>
          <option value="">All categories</option>
          {#each list as c}<option value={c}>{c}</option>{/each}
        </select>
      {/await}
    </div>
  </div>

  {#if loadError}
    <p class="error">Could not load entries — is <code>tlserve</code> running?</p>
  {:else if loading}
    <p class="muted">Loading…</p>
  {:else if filtered.length === 0}
    <p class="empty">No entries found.</p>
  {:else}
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Project</th>
            <th>Category</th>
            <th>Description</th>
            <th>Hours</th>
          </tr>
        </thead>
        <tbody>
          {#each filtered as entry (entry.id)}
            <tr>
              <td class="mono">{entry.date}</td>
              <td class="bold">{entry.project}</td>
              <td><span class="badge">{entry.category}</span></td>
              <td class="muted">{entry.description || '—'}</td>
              <td class="hours">{entry.hours.toFixed(2)}</td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>

    <div class="footer">
      <p class="count">{filtered.length} {filtered.length === 1 ? 'entry' : 'entries'}</p>
      <p class="total">Total: <span>{totalHours.toFixed(2)} hrs</span></p>
    </div>
  {/if}
</div>

<style>
  .page {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  h1 {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
  }

  .btn-primary {
    background: #6366f1;
    color: #fff;
    text-decoration: none;
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: background 0.15s;
  }

  .btn-primary:hover { background: #4f46e5; }

  .filters {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .filter-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    flex-wrap: wrap;
  }

  .filter-row button {
    background: #1a1d27;
    border: 1px solid #2d3148;
    color: #94a3b8;
    padding: 0.35rem 0.85rem;
    border-radius: 6px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.15s;
  }

  .filter-row button:hover  { border-color: #6366f1; color: #e2e8f0; }
  .filter-row button.active { background: #6366f1; border-color: #6366f1; color: #fff; }

  .filter-row input[type='month'],
  .filter-row select {
    background: #1a1d27;
    border: 1px solid #2d3148;
    color: #e2e8f0;
    padding: 0.35rem 0.6rem;
    border-radius: 6px;
    font-size: 0.85rem;
    outline: none;
    cursor: pointer;
  }

  .filter-row select:focus,
  .filter-row input[type='month']:focus { border-color: #6366f1; }

  .table-wrap {
    background: #1a1d27;
    border: 1px solid #2d3148;
    border-radius: 10px;
    overflow: hidden;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }

  thead th {
    text-align: left;
    padding: 0.75rem 1rem;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: #64748b;
    border-bottom: 1px solid #2d3148;
  }

  tbody tr:not(:last-child) { border-bottom: 1px solid #1e2235; }

  tbody td {
    padding: 0.75rem 1rem;
    color: #cbd5e1;
  }

  .bold  { font-weight: 600; color: #e2e8f0; }
  .mono  { font-variant-numeric: tabular-nums; font-size: 0.85rem; color: #64748b; }
  .hours { font-variant-numeric: tabular-nums; font-weight: 600; color: #6366f1; }

  .badge {
    background: #2d3148;
    color: #94a3b8;
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.78rem;
  }

  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .count { font-size: 0.82rem; color: #64748b; }

  .total { font-size: 0.9rem; color: #94a3b8; }
  .total span { font-weight: 600; color: #6366f1; font-variant-numeric: tabular-nums; }

  .muted { color: #64748b; }
  .empty { color: #64748b; font-size: 0.9rem; }
  .error { color: #f87171; font-size: 0.9rem; }

  code {
    background: #2d3148;
    padding: 0.1em 0.4em;
    border-radius: 4px;
    font-size: 0.85em;
  }
</style>
