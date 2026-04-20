<script lang="ts">
  import { api, type Entry } from '$lib/api';

  let allEntries  = $state<Entry[]>([]);
  let loading     = $state(true);
  let loadError   = $state(false);

  let dateFilter   = $state('all');
  let month        = $state('');
  let project      = $state('');
  let category     = $state('');
  let dateAsc      = $state(false);
  let selectedDate = $state('');

  function pickDate(date: string) {
    selectedDate = selectedDate === date ? '' : date;
  }

  function clearDateFilter(filter: string) {
    selectedDate = '';
    dateFilter = filter;
  }

  const projects   = api.projects();
  const categories = api.categories();

  const today     = new Date().toISOString().split('T')[0];
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

  api.entries.all()
    .then(e  => { allEntries = e; loading = false; })
    .catch(() => { loadError = true; loading = false; });

  let filtered = $derived.by(() => {
    const rows = allEntries.filter(e => {
      if (selectedDate && e.date !== selectedDate)                           return false;
      if (!selectedDate && dateFilter === 'today'     && e.date !== today)  return false;
      if (!selectedDate && dateFilter === 'yesterday' && e.date !== yesterday) return false;
      if (!selectedDate && dateFilter === 'month'     && month && !e.date.startsWith(month)) return false;
      if (project  && e.project  !== project)                               return false;
      if (category && e.category !== category)                              return false;
      return true;
    });
    return dateAsc
      ? rows
      : [...rows].reverse();
  });

  let totalHours = $derived(filtered.reduce((s, e) => s + e.hours, 0));
</script>

<div class="page">
  <div class="page-header">
    <h1>Entries</h1>
    <a href="/log" class="btn-primary">+ Log Time</a>
  </div>

  <div class="filters">
    <div class="filter-row">
      <button class:active={dateFilter === 'all' && !selectedDate}       onclick={() => clearDateFilter('all')}>All</button>
      <button class:active={dateFilter === 'today' && !selectedDate}     onclick={() => clearDateFilter('today')}>Today</button>
      <button class:active={dateFilter === 'yesterday' && !selectedDate} onclick={() => clearDateFilter('yesterday')}>Yesterday</button>
      <button class:active={dateFilter === 'month' && !selectedDate}     onclick={() => { if (dateFilter === 'month') clearDateFilter('all'); else clearDateFilter('month'); }}>Date</button>
      {#if dateFilter === 'month' && !selectedDate}
        <div class="date-input-wrap">
          <input type="text" bind:value={month} placeholder={today} />
          <input type="date" class="date-picker-hidden"
            onchange={(e) => { pickDate((e.target as HTMLInputElement).value); (e.target as HTMLInputElement).value = ''; }} />
          <button class="calendar-icon" onclick={(e) => (e.currentTarget.previousElementSibling as HTMLInputElement).showPicker()} title="Pick a day">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </button>
        </div>
      {/if}
      {#if selectedDate}
        <span class="date-chip">{selectedDate} <button onclick={() => selectedDate = ''}>×</button></span>
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
            <th class="sortable" onclick={() => dateAsc = !dateAsc}>
              Date <span class="sort-icon">{dateAsc ? '↑' : '↓'}</span>
            </th>
            <th>Project</th>
            <th>Category</th>
            <th>Description</th>
            <th>Hours</th>
          </tr>
        </thead>
        <tbody>
          {#each filtered as entry (entry.id)}
            <tr>
              <td class="mono date-cell" class:date-active={selectedDate === entry.date} onclick={() => pickDate(entry.date)}>{entry.date}</td>
              <td class="bold project-cell" onclick={() => project = project === entry.project ? '' : entry.project}>{entry.project}</td>
              <td><span class="badge category-cell" onclick={() => category = category === entry.category ? '' : entry.category}>{entry.category}</span></td>
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
    background: var(--accent);
    color: #fff;
    text-decoration: none;
    padding: 0.4rem 0.9rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: background 0.15s;
  }

  .btn-primary:hover { background: var(--accent-hover); }

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
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text-muted-mid);
    padding: 0.35rem 0.85rem;
    border-radius: 6px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.15s;
  }

  .filter-row button:hover  { border-color: var(--accent); color: var(--text); }
  .filter-row button.active { background: var(--accent); border-color: var(--accent); color: #fff; }

  .filter-row select,
  .date-input-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 0.35rem 0.6rem;
    border-radius: 6px;
    font-size: 0.85rem;
    outline: none;
    cursor: pointer;
  }

  .filter-row select:focus { border-color: var(--accent); }

  .date-input-wrap {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0;
    cursor: default;
  }

  .date-input-wrap:focus-within { border-color: var(--accent); }

  .date-input-wrap input[type='text'] {
    background: none;
    border: none;
    color: var(--text);
    font-size: 0.85rem;
    outline: none;
    padding: 0.35rem 0.6rem;
    width: 7.5rem;
  }

  .date-picker-hidden {
    position: absolute;
    opacity: 0;
    pointer-events: none;
    width: 0;
    height: 0;
  }

  .calendar-icon {
    background: none;
    border: none;
    color: var(--text-muted);
    cursor: pointer;
    padding: 0.35rem 0.5rem 0.35rem 0;
    display: flex;
    align-items: center;
    transition: color 0.15s;
  }

  .calendar-icon:hover { color: var(--accent-light); }

  .table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
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
    color: var(--text-muted);
    border-bottom: 1px solid var(--border);
  }

  thead th.sortable {
    cursor: pointer;
    user-select: none;
  }

  thead th.sortable:hover { color: var(--text); }

  .sort-icon { color: var(--accent); }

  tbody tr:not(:last-child) { border-bottom: 1px solid var(--border-subtle); }

  tbody td {
    padding: 0.75rem 1rem;
    color: var(--text-secondary);
  }

  .bold  { font-weight: 600; color: var(--text); white-space: nowrap; }

  .project-cell { cursor: pointer; }
  .project-cell:hover { color: var(--accent-light); }

  .category-cell { cursor: pointer; white-space: nowrap; }
  .category-cell:hover { background: var(--badge-hover); color: var(--text); }
  .mono  { font-variant-numeric: tabular-nums; font-size: 0.85rem; color: var(--text-muted); white-space: nowrap; }
  .hours { font-variant-numeric: tabular-nums; font-weight: 600; color: var(--accent); }

  .date-cell { cursor: pointer; }
  .date-cell:hover { color: var(--accent-light); }
  .date-active { color: var(--accent) !important; font-weight: 600; }

  .date-chip {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    background: var(--surface2);
    color: var(--accent-light);
    border: 1px solid var(--accent);
    border-radius: 6px;
    padding: 0.2rem 0.5rem;
    font-size: 0.82rem;
    font-variant-numeric: tabular-nums;
  }

  .date-chip button {
    background: none;
    border: none;
    color: var(--text-muted-mid);
    cursor: pointer;
    padding: 0;
    font-size: 1rem;
    line-height: 1;
  }

  .date-chip button:hover { color: var(--error); }

  .badge {
    background: var(--surface2);
    color: var(--text-muted-mid);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.78rem;
  }

  .footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .count { font-size: 0.82rem; color: var(--text-muted); }

  .total { font-size: 0.9rem; color: var(--text-muted-mid); }
  .total span { font-weight: 600; color: var(--accent); font-variant-numeric: tabular-nums; }

  .muted { color: var(--text-muted); }
  .empty { color: var(--text-muted); font-size: 0.9rem; }
  .error { color: var(--error); font-size: 0.9rem; }

  code {
    background: var(--surface2);
    padding: 0.1em 0.4em;
    border-radius: 4px;
    font-size: 0.85em;
  }
</style>
