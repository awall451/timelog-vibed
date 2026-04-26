<script lang="ts">
  import { api, type Entry, type ProjectSum } from '$lib/api';
  import { settings } from '$lib/settings.svelte';

  const todayEntries   = api.entries.today();
  const todayHours     = api.sum.today();
  const projectTotals  = api.sum.perProject();
</script>

<div class="dashboard">
  <div class="page-header">
    <h1>Dashboard</h1>
    <p class="date">{new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
  </div>

  <!-- Today's hours stat -->
  {#await todayHours}
    <div class="stat-card loading">—</div>
  {:then { hours }}
    <div class="stat-card">
      <span class="stat-label">Hours today</span>
      <span
        class="stat-value"
        class:on-track={hours >= settings.dailyGoalHours * 0.75}
        class:low={hours < settings.dailyGoalHours * 0.5}
      >
        {hours.toFixed(2)}
      </span>
      <span class="stat-sub">of {settings.dailyGoalHours.toFixed(2)} goal</span>
    </div>
  {/await}

  <!-- Today's entries -->
  <section class="section">
    <div class="section-header">
      <h2>Today's Entries</h2>
      <a href="/log" class="btn-primary">+ Log Time</a>
    </div>

    {#await todayEntries}
      <p class="muted">Loading…</p>
    {:then entries}
      {#if entries.length === 0}
        <p class="empty">No entries yet today. <a href="/log">Log some time →</a></p>
      {:else}
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Project</th>
                <th>Category</th>
                <th>Description</th>
                <th>Hours</th>
              </tr>
            </thead>
            <tbody>
              {#each entries as entry (entry.id)}
                <tr>
                  <td class="bold">{entry.project}</td>
                  <td><span class="badge">{entry.category}</span></td>
                  <td class="muted">{entry.description || '—'}</td>
                  <td class="hours">{entry.hours.toFixed(2)}</td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    {:catch}
      <p class="error">Could not load entries — is <code>tlserve</code> running?</p>
    {/await}
  </section>

  <!-- Hours by project -->
  <section class="section">
    <h2>Hours by Project <span class="muted small">(all time)</span></h2>

    {#await projectTotals}
      <p class="muted">Loading…</p>
    {:then projects}
      {#if projects.length === 0}
        <p class="empty">No data yet.</p>
      {:else}
        {@const max = Math.max(...projects.map((p: ProjectSum) => p.hours))}
        <div class="bar-list">
          {#each projects as p (p.project)}
            <div class="bar-row">
              <span class="bar-label">{p.project}</span>
              <div class="bar-track">
                <div class="bar-fill" style="width: {(p.hours / max) * 100}%"></div>
              </div>
              <span class="bar-value">{p.hours.toFixed(1)}h</span>
            </div>
          {/each}
        </div>
      {/if}
    {:catch}
      <p class="error">Could not load project data.</p>
    {/await}
  </section>
</div>

<style>
  .dashboard {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }

  .page-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
  }

  .page-header .date {
    color: var(--text-muted);
    font-size: 0.9rem;
    margin-top: 0.25rem;
  }

  /* Stat card */
  .stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem 2rem;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    width: fit-content;
    min-width: 180px;
  }

  .stat-label {
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
  }

  .stat-value {
    font-size: 3rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    color: var(--accent);
    line-height: 1;
  }

  .stat-value.on-track { color: var(--success); }
  .stat-value.low      { color: var(--warning); }

  .stat-sub {
    font-size: 0.8rem;
    color: var(--text-muted);
  }

  /* Sections */
  .section {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  h2 {
    font-size: 1.1rem;
    font-weight: 600;
    letter-spacing: -0.02em;
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

  /* Table */
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

  tbody tr:not(:last-child) {
    border-bottom: 1px solid var(--border-subtle);
  }

  tbody td {
    padding: 0.75rem 1rem;
    color: var(--text-secondary);
  }

  .bold { font-weight: 600; color: var(--text); }

  .badge {
    background: var(--surface2);
    color: var(--text-muted-mid);
    padding: 0.2rem 0.5rem;
    border-radius: 4px;
    font-size: 0.78rem;
    white-space: nowrap;
  }

  .hours {
    font-variant-numeric: tabular-nums;
    font-weight: 600;
    color: var(--accent);
  }

  /* Bar chart */
  .bar-list {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }

  .bar-row {
    display: grid;
    grid-template-columns: 160px 1fr 52px;
    align-items: center;
    gap: 0.75rem;
  }

  .bar-label {
    font-size: 0.88rem;
    color: var(--text-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .bar-track {
    background: var(--surface);
    border-radius: 4px;
    height: 8px;
    overflow: hidden;
  }

  .bar-fill {
    background: var(--accent);
    height: 100%;
    border-radius: 4px;
    transition: width 0.4s ease;
  }

  .bar-value {
    font-size: 0.82rem;
    color: var(--text-muted);
    text-align: right;
    font-variant-numeric: tabular-nums;
  }

  /* Utility */
  .muted { color: var(--text-muted); }
  .small { font-size: 0.8rem; font-weight: 400; }
  .empty { color: var(--text-muted); font-size: 0.9rem; }
  .empty a { color: var(--accent); text-decoration: none; }
  .error { color: var(--error); font-size: 0.9rem; }
  .loading { color: var(--text-muted); }

  code {
    background: var(--surface2);
    padding: 0.1em 0.4em;
    border-radius: 4px;
    font-size: 0.85em;
  }
</style>
