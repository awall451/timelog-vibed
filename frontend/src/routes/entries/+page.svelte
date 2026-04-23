<script lang="ts">
  import { api, type Entry, type NewEntry } from '$lib/api';

  let allEntries  = $state<Entry[]>([]);
  let loading     = $state(true);
  let loadError   = $state(false);

  let dateFilter   = $state('all');
  let month        = $state('');
  let project      = $state('');
  let category     = $state('');
  let dateAsc      = $state(false);
  let selectedDate = $state('');

  const CELL    = 11;
  const GAP     = 2;
  const STEP    = CELL + GAP;
  const LABEL_H = 14;
  const WEEKS   = 53;
  const SVG_W   = WEEKS * STEP;
  const SVG_H   = LABEL_H + 7 * STEP;
  const FILL_OP = [1, 0.22, 0.45, 0.7, 1];

  let tooltip = $state<{ text: string; x: number; y: number } | null>(null);

  // row action state
  let hoveredId  = $state<number | null>(null);
  let menuId     = $state<number | null>(null);
  let deleteId   = $state<number | null>(null);
  let deleting   = $state(false);

  // edit modal state
  let editEntry    = $state<Entry | null>(null);
  let editProject  = $state('');
  let editCategory = $state('');
  let editDesc     = $state('');
  let editHours    = $state('');
  let editDate     = $state('');
  let editSaving   = $state(false);
  let editError    = $state('');

  function pickDate(date: string) {
    selectedDate = selectedDate === date ? '' : date;
  }

  function clearDateFilter(filter: string) {
    selectedDate = '';
    dateFilter = filter;
  }

  const projectSuggestions  = api.projects();
  const categorySuggestions = api.categories();

  const today     = new Date().toISOString().split('T')[0];
  const yesterday = new Date(Date.now() - 86400000).toISOString().split('T')[0];

  async function loadEntries() {
    allEntries = await api.entries.all();
  }

  loadEntries()
    .then(() => { loading = false; })
    .catch(() => { loadError = true; loading = false; });

  let filtered = $derived.by(() => {
    const rows = allEntries.filter(e => {
      if (selectedDate && e.date !== selectedDate)                              return false;
      if (!selectedDate && dateFilter === 'today'     && e.date !== today)     return false;
      if (!selectedDate && dateFilter === 'yesterday' && e.date !== yesterday) return false;
      if (!selectedDate && dateFilter === 'month'     && month && !e.date.startsWith(month)) return false;
      if (project  && e.project  !== project)                                  return false;
      if (category && e.category !== category)                                 return false;
      return true;
    });
    return dateAsc ? rows : [...rows].reverse();
  });

  let totalHours = $derived(filtered.reduce((s, e) => s + e.hours, 0));

  let heatmapHours = $derived.by(() => {
    const m = new Map<string, number>();
    for (const e of allEntries) {
      if (project  && e.project  !== project)  continue;
      if (category && e.category !== category) continue;
      m.set(e.date, (m.get(e.date) ?? 0) + e.hours);
    }
    return m;
  });

  let gridData = $derived.by(() => {
    const todayDate = new Date(today + 'T00:00:00');
    const todayDow  = todayDate.getDay();
    const startDate = new Date(todayDate);
    startDate.setDate(startDate.getDate() - 364 - todayDow);

    type Cell = { date: string; hours: number; level: number; inRange: boolean; col: number; row: number };
    const cells: Cell[] = [];

    for (let i = 0; i < WEEKS * 7; i++) {
      const d = new Date(startDate);
      d.setDate(d.getDate() + i);
      const dateStr = d.toISOString().split('T')[0];
      const hrs     = heatmapHours.get(dateStr) ?? 0;
      const level   = hrs === 0 ? 0 : hrs < 2 ? 1 : hrs < 4 ? 2 : hrs < 6 ? 3 : 4;
      cells.push({
        date: dateStr, hours: hrs, level,
        inRange: dateStr <= today,
        col: Math.floor(i / 7),
        row: i % 7
      });
    }

    const monthLabels: Array<{ col: number; label: string }> = [];
    let lastMonth = '';
    for (let col = 0; col < WEEKS; col++) {
      const mo = cells[col * 7].date.slice(0, 7);
      if (mo !== lastMonth) {
        lastMonth = mo;
        monthLabels.push({
          col,
          label: new Date(cells[col * 7].date + 'T12:00:00').toLocaleDateString('en-US', { month: 'short' })
        });
      }
    }

    return { cells, monthLabels };
  });

  function openMenu(id: number) {
    menuId   = menuId === id ? null : id;
    deleteId = null;
  }

  function closeMenu() {
    menuId   = null;
    deleteId = null;
  }

  function openEdit(entry: Entry) {
    editEntry    = entry;
    editProject  = entry.project;
    editCategory = entry.category;
    editDesc     = entry.description ?? '';
    editHours    = String(entry.hours);
    editDate     = entry.date;
    editError    = '';
    closeMenu();
  }

  function closeEdit() {
    editEntry = null;
  }

  async function saveEdit(e: Event) {
    e.preventDefault();
    if (!editEntry) return;
    editError = '';
    const h = parseFloat(editHours);
    if (!editProject || !editCategory || isNaN(h) || h <= 0) {
      editError = 'Project, category, and positive hours required.';
      return;
    }
    editSaving = true;
    try {
      const updated = await api.entries.update(editEntry.id, {
        project: editProject,
        category: editCategory,
        description: editDesc,
        hours: h,
        date: editDate,
      } as NewEntry);
      allEntries = allEntries
        .map(en => en.id === updated.id ? updated : en)
        .sort((a, b) => a.date < b.date ? -1 : a.date > b.date ? 1 : a.id - b.id);
      closeEdit();
    } catch {
      editError = 'Save failed.';
    } finally {
      editSaving = false;
    }
  }

  function confirmDelete(id: number) {
    deleteId = id;
    menuId   = id;
  }

  async function doDelete() {
    if (!deleteId) return;
    deleting = true;
    try {
      await api.entries.delete(deleteId);
      allEntries = allEntries.filter(e => e.id !== deleteId);
      closeMenu();
    } catch {
      // silent — entry stays in list
    } finally {
      deleting = false;
    }
  }
</script>

<svelte:window onclick={(e) => {
  if (menuId !== null && !(e.target as Element).closest('.row-menu')) closeMenu();
}} />

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
      {#await projectSuggestions then list}
        <select bind:value={project}>
          <option value="">All projects</option>
          {#each list as p}<option value={p}>{p}</option>{/each}
        </select>
      {/await}

      {#await categorySuggestions then list}
        <select bind:value={category}>
          <option value="">All categories</option>
          {#each list as c}<option value={c}>{c}</option>{/each}
        </select>
      {/await}
    </div>
  </div>

  {#if !loading && !loadError}
    <div class="heatmap-section">
      <svg
        viewBox="0 0 {SVG_W} {SVG_H}"
        style="width:100%; max-width:{SVG_W}px; display:block; overflow:visible"
        aria-label="Activity heatmap — last 12 months"
        role="img"
      >
        {#each gridData.monthLabels as { col, label } (col)}
          <text
            x={col * STEP}
            y={10}
            style="font-size:9px; fill:var(--text-muted); font-family:inherit"
          >{label}</text>
        {/each}

        {#each gridData.cells as cell (cell.date)}
          <rect
            x={cell.col * STEP}
            y={LABEL_H + cell.row * STEP}
            width={CELL}
            height={CELL}
            rx="2"
            fill={cell.level > 0 && cell.inRange ? 'var(--accent)' : 'var(--surface2)'}
            fill-opacity={cell.level > 0 && cell.inRange ? FILL_OP[cell.level] : 1}
            stroke={selectedDate === cell.date ? 'var(--text)' : 'none'}
            stroke-width="1.5"
            style="cursor:{cell.inRange ? 'pointer' : 'default'}"
            onclick={() => { if (cell.inRange) pickDate(cell.date); }}
            onmouseenter={(e) => {
              if (!cell.inRange) return;
              tooltip = {
                text: cell.hours > 0
                  ? `${cell.date} — ${cell.hours.toFixed(1)}h`
                  : `${cell.date} — no activity`,
                x: e.clientX + 12,
                y: e.clientY - 36
              };
            }}
            onmouseleave={() => (tooltip = null)}
          />
        {/each}
      </svg>

      <div class="heat-legend">
        <span class="legend-label">Less</span>
        {#each [0, 1, 2, 3, 4] as lvl}
          <svg width={CELL} height={CELL} viewBox="0 0 {CELL} {CELL}" style="display:block">
            <rect
              width={CELL} height={CELL} rx="2"
              fill={lvl > 0 ? 'var(--accent)' : 'var(--surface2)'}
              fill-opacity={lvl > 0 ? FILL_OP[lvl] : 1}
            />
          </svg>
        {/each}
        <span class="legend-label">More</span>
      </div>
    </div>
  {/if}

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
            <th class="actions-col"></th>
          </tr>
        </thead>
        <tbody>
          {#each filtered as entry (entry.id)}
            <tr
              onmouseenter={() => hoveredId = entry.id}
              onmouseleave={() => { if (menuId !== entry.id) hoveredId = null; }}
            >
              <td class="mono date-cell" class:date-active={selectedDate === entry.date} onclick={() => pickDate(entry.date)}>{entry.date}</td>
              <td class="bold project-cell" onclick={() => project = project === entry.project ? '' : entry.project}>{entry.project}</td>
              <td><span class="badge category-cell" onclick={() => category = category === entry.category ? '' : entry.category}>{entry.category}</span></td>
              <td class="muted">{entry.description || '—'}</td>
              <td class="hours">{entry.hours.toFixed(2)}</td>
              <td class="actions-col">
                <div class="row-menu">
                  <button
                    class="ellipsis-btn"
                    class:visible={hoveredId === entry.id || menuId === entry.id}
                    onclick={(e) => { e.stopPropagation(); openMenu(entry.id); }}
                    aria-label="Row actions"
                  >⋮</button>

                  {#if menuId === entry.id}
                    <div class="dropdown">
                      {#if deleteId === entry.id}
                        <div class="delete-confirm">
                          <span>Delete?</span>
                          <button class="confirm-yes" onclick={(e) => { e.stopPropagation(); doDelete(); }} disabled={deleting}>
                            {deleting ? '…' : 'Yes'}
                          </button>
                          <button class="confirm-no" onclick={(e) => { e.stopPropagation(); closeMenu(); }}>No</button>
                        </div>
                      {:else}
                        <button onclick={(e) => { e.stopPropagation(); openEdit(entry); }}>Edit</button>
                        <button class="danger" onclick={(e) => { e.stopPropagation(); confirmDelete(entry.id); }}>Delete</button>
                      {/if}
                    </div>
                  {/if}
                </div>
              </td>
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

{#if tooltip}
  <div class="hm-tooltip" style="left:{tooltip.x}px;top:{tooltip.y}px">{tooltip.text}</div>
{/if}

<!-- Edit modal -->
{#if editEntry}
  <div class="modal-backdrop" onclick={closeEdit} role="presentation">
    <div class="modal" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-label="Edit entry">
      <h2>Edit Entry</h2>

      <form onsubmit={saveEdit}>
        {#if editError}
          <p class="edit-error">{editError}</p>
        {/if}

        <div class="field">
          <label for="edit-project">Project</label>
          {#await projectSuggestions then list}
            <input id="edit-project" list="edit-project-list" bind:value={editProject} autocomplete="off" />
            <datalist id="edit-project-list">
              {#each list as p}<option value={p}></option>{/each}
            </datalist>
          {:catch}
            <input id="edit-project" bind:value={editProject} />
          {/await}
        </div>

        <div class="field">
          <label for="edit-category">Category</label>
          {#await categorySuggestions then list}
            <input id="edit-category" list="edit-category-list" bind:value={editCategory} autocomplete="off" />
            <datalist id="edit-category-list">
              {#each list as c}<option value={c}></option>{/each}
            </datalist>
          {:catch}
            <input id="edit-category" bind:value={editCategory} />
          {/await}
        </div>

        <div class="field">
          <label for="edit-desc">Description <span class="optional">(optional)</span></label>
          <input id="edit-desc" bind:value={editDesc} />
        </div>

        <div class="field-row">
          <div class="field">
            <label for="edit-hours">Hours</label>
            <input id="edit-hours" type="number" step="0.25" min="0.25" bind:value={editHours} />
          </div>
          <div class="field">
            <label for="edit-date">Date</label>
            <input id="edit-date" type="date" bind:value={editDate} />
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" onclick={closeEdit}>Cancel</button>
          <button type="submit" class="btn-primary" disabled={editSaving}>
            {editSaving ? 'Saving…' : 'Save'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

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

  /* heatmap */
  .heatmap-section {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
  }

  .heat-legend {
    display: flex;
    align-items: center;
    gap: 0.3rem;
    justify-content: flex-end;
  }

  .legend-label {
    font-size: 0.72rem;
    color: var(--text-muted);
    margin: 0 0.15rem;
  }

  .hm-tooltip {
    position: fixed;
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 0.25rem 0.5rem;
    border-radius: 5px;
    font-size: 0.78rem;
    pointer-events: none;
    z-index: 1000;
    white-space: nowrap;
    font-variant-numeric: tabular-nums;
  }

  /* table */
  .table-wrap {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: visible;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
  }

  thead tr:first-child th:first-child { border-radius: 10px 0 0 0; }
  thead tr:first-child th:last-child  { border-radius: 0 10px 0 0; }
  tbody tr:last-child  td:first-child { border-radius: 0 0 0 10px; }
  tbody tr:last-child  td:last-child  { border-radius: 0 0 10px 0; }

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

  /* row actions */
  .actions-col {
    width: 2rem;
    padding: 0 0.5rem 0 0 !important;
    text-align: right;
  }

  .row-menu {
    position: relative;
    display: inline-block;
  }

  .ellipsis-btn {
    background: none;
    border: none;
    color: var(--text-muted);
    font-size: 1.1rem;
    line-height: 1;
    padding: 0.2rem 0.3rem;
    border-radius: 4px;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.1s, background 0.1s;
  }

  .ellipsis-btn.visible { opacity: 1; }
  .ellipsis-btn:hover { background: var(--surface2); color: var(--text); }

  .dropdown {
    position: absolute;
    right: 0;
    top: calc(100% + 4px);
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    z-index: 200;
    min-width: 7rem;
    overflow: hidden;
  }

  .dropdown button {
    display: block;
    width: 100%;
    background: none;
    border: none;
    color: var(--text);
    padding: 0.55rem 0.9rem;
    text-align: left;
    font-size: 0.88rem;
    cursor: pointer;
    transition: background 0.1s;
  }

  .dropdown button:hover { background: var(--surface2); }
  .dropdown button.danger { color: var(--error); }
  .dropdown button.danger:hover { background: var(--error-bg); }

  .delete-confirm {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.5rem 0.75rem;
    white-space: nowrap;
  }

  .delete-confirm span {
    font-size: 0.85rem;
    color: var(--text-muted-mid);
    flex: 1;
  }

  .confirm-yes, .confirm-no {
    padding: 0.25rem 0.55rem !important;
    border-radius: 5px;
    font-size: 0.8rem !important;
    font-weight: 600;
    width: auto !important;
  }

  .confirm-yes {
    background: var(--error) !important;
    color: #fff !important;
  }

  .confirm-yes:hover:not(:disabled) { opacity: 0.85; }
  .confirm-yes:disabled { opacity: 0.5; cursor: not-allowed; }

  .confirm-no {
    background: var(--surface2) !important;
    color: var(--text-muted-mid) !important;
  }

  .confirm-no:hover { background: var(--border) !important; }

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

  /* edit modal */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 500;
  }

  .modal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.75rem;
    width: min(480px, 92vw);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  }

  .modal h2 {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 1.25rem;
    letter-spacing: -0.02em;
  }

  .modal form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .field {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    flex: 1;
  }

  .field label {
    font-size: 0.78rem;
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

  .field input {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 7px;
    color: var(--text);
    padding: 0.55rem 0.75rem;
    font-size: 0.9rem;
    outline: none;
    width: 100%;
    transition: border-color 0.15s;
  }

  .field input:focus { border-color: var(--accent); }

  .field-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.75rem;
  }

  .modal-actions {
    display: flex;
    gap: 0.6rem;
    justify-content: flex-end;
    margin-top: 0.5rem;
  }

  .btn-secondary {
    background: transparent;
    color: var(--text-muted-mid);
    padding: 0.55rem 1.1rem;
    border-radius: 7px;
    font-size: 0.88rem;
    border: 1px solid var(--border);
    cursor: pointer;
    transition: border-color 0.15s;
    text-decoration: none;
  }

  .btn-secondary:hover { border-color: var(--text-muted-mid); }

  .modal .btn-primary {
    background: var(--accent);
    color: #fff;
    border: none;
    padding: 0.55rem 1.2rem;
    border-radius: 7px;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.15s;
    text-decoration: none;
  }

  .modal .btn-primary:hover:not(:disabled) { background: var(--accent-hover); }
  .modal .btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

  .edit-error {
    background: var(--error-bg);
    border: 1px solid var(--error-border);
    color: var(--error);
    padding: 0.5rem 0.75rem;
    border-radius: 7px;
    font-size: 0.85rem;
    margin-bottom: 0.25rem;
  }
</style>
