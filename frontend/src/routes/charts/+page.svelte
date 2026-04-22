<script lang="ts">
  import { api, type Entry } from '$lib/api';

  let allEntries = $state<Entry[]>([]);
  let loading    = $state(true);
  let loadError  = $state(false);

  const todayStr  = new Date().toISOString().split('T')[0];
  const ninetyAgo = new Date(Date.now() - 89 * 86400000).toISOString().split('T')[0];

  let rangeStart = $state(ninetyAgo);
  let rangeEnd   = $state(todayStr);

  api.entries.all()
    .then(e  => { allEntries = e; loading = false; })
    .catch(() => { loadError = true; loading = false; });

  const PALETTE = ['#6366f1','#22c55e','#f59e0b','#ec4899','#06b6d4','#f97316','#84cc16','#a855f7','#14b8a6','#ef4444'];
  const pc = (i: number) => PALETTE[i % PALETTE.length];

  let scoped = $derived(allEntries.filter(e => e.date >= rangeStart && e.date <= rangeEnd));

  let byProject = $derived.by(() => {
    const m = new Map<string, number>();
    for (const e of scoped) m.set(e.project, (m.get(e.project) ?? 0) + e.hours);
    return [...m.entries()].sort((a, b) => b[1] - a[1]).map(([name, hours]) => ({ name, hours }));
  });

  let byCategory = $derived.by(() => {
    const m = new Map<string, number>();
    for (const e of scoped) m.set(e.category, (m.get(e.category) ?? 0) + e.hours);
    return [...m.entries()].sort((a, b) => b[1] - a[1]).map(([name, hours]) => ({ name, hours }));
  });

  function donutSegments(data: { name: string; hours: number }[]) {
    const total = data.reduce((s, d) => s + d.hours, 0);
    if (total === 0) return { segs: [], total: 0 };
    const cx = 100, cy = 100, r = 72, ri = 48;
    let angle = -Math.PI / 2;
    const segs = data.map((d, i) => {
      const frac  = d.hours / total;
      const sweep = frac * 2 * Math.PI;
      const a1 = angle, a2 = angle + sweep;
      const large = sweep > Math.PI ? 1 : 0;
      const path = [
        `M ${cx + r * Math.cos(a1)} ${cy + r * Math.sin(a1)}`,
        `A ${r} ${r} 0 ${large} 1 ${cx + r * Math.cos(a2)} ${cy + r * Math.sin(a2)}`,
        `L ${cx + ri * Math.cos(a2)} ${cy + ri * Math.sin(a2)}`,
        `A ${ri} ${ri} 0 ${large} 0 ${cx + ri * Math.cos(a1)} ${cy + ri * Math.sin(a1)}`,
        'Z'
      ].join(' ');
      angle = a2;
      return { path, color: pc(i), name: d.name, hours: d.hours, pct: Math.round(frac * 100) };
    });
    return { segs, total };
  }

  let projectDonut  = $derived(donutSegments(byProject));
  let categoryDonut = $derived(donutSegments(byCategory));

  // ── Stacked bar — last 14 days ──────────────────────────────────────────────
  const BAR_W = 28, BAR_STEP = 34;
  const BAR_DAYS = 14;
  const BP_L = 36, BP_R = 10, BP_T = 10, BP_B = 28;
  const BAR_H = 180;
  const B_SVG_W = BP_L + BAR_DAYS * BAR_STEP - 6 + BP_R;
  const B_SVG_H = BP_T + BAR_H + BP_B;

  let stackedData = $derived.by(() => {
    const days: string[] = [];
    for (let i = BAR_DAYS - 1; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86400000);
      days.push(d.toISOString().split('T')[0]);
    }
    const allProjects = [...new Set(allEntries.map(e => e.project))].sort();
    const pidx = Object.fromEntries(allProjects.map((p, i) => [p, i]));
    const dayData = days.map(date => {
      const byProj: Record<string, number> = {};
      for (const e of allEntries) if (e.date === date) byProj[e.project] = (byProj[e.project] ?? 0) + e.hours;
      const total = Object.values(byProj).reduce((s, h) => s + h, 0);
      return { date, byProj, total };
    });
    const maxH = Math.max(...dayData.map(d => d.total), 1);
    const bars = dayData.map((day, di) => {
      const x = BP_L + di * BAR_STEP;
      let cumH = 0;
      const segs = allProjects.filter(p => (day.byProj[p] ?? 0) > 0).map(p => {
        const h = day.byProj[p];
        const segH = Math.max(BAR_H * h / maxH, 1);
        const y = BP_T + BAR_H * (1 - (cumH + h) / maxH);
        cumH += h;
        return { p, h, y, segH, color: pc(pidx[p]) };
      });
      return { date: day.date, total: day.total, x, segs };
    });
    return { allProjects, pidx, maxH, bars };
  });

  // ── Pace line — last 28 days ────────────────────────────────────────────────
  const LINE_DAYS = 28;
  const LP_L = 36, LP_R = 14, LP_T = 12, LP_B = 28;
  const LC_W = 580, LC_H = 140;
  const L_SVG_W = LP_L + LC_W + LP_R;
  const L_SVG_H = LP_T + LC_H + LP_B;
  const GOAL = 8;

  let paceData = $derived.by(() => {
    const days: { date: string; hours: number }[] = [];
    for (let i = LINE_DAYS - 1; i >= 0; i--) {
      const d = new Date(Date.now() - i * 86400000);
      const date = d.toISOString().split('T')[0];
      const hours = allEntries.filter(e => e.date === date).reduce((s, e) => s + e.hours, 0);
      days.push({ date, hours });
    }
    const maxH = Math.max(...days.map(d => d.hours), GOAL);
    const xStep = LC_W / (LINE_DAYS - 1);
    const pts = days.map((d, i) => ({
      ...d,
      x: LP_L + i * xStep,
      y: LP_T + LC_H * (1 - d.hours / maxH)
    }));
    const goalY = LP_T + LC_H * (1 - GOAL / maxH);
    const polyline = pts.map(p => `${p.x},${p.y}`).join(' ');
    const areaD = `M ${pts[0].x} ${LP_T + LC_H} ${pts.map(p => `L ${p.x} ${p.y}`).join(' ')} L ${pts[pts.length - 1].x} ${LP_T + LC_H} Z`;
    const xLabels = [0, 7, 14, 21, 27].map(i => ({ x: LP_L + i * xStep, label: days[i].date.slice(5) }));
    return { pts, polyline, areaD, goalY, maxH, xLabels };
  });

  // ── Project × Category matrix ───────────────────────────────────────────────
  let pcMatrix = $derived.by(() => {
    const projects   = [...new Set(scoped.map(e => e.project))].sort();
    const categories = [...new Set(scoped.map(e => e.category))].sort();
    const grid: number[][] = projects.map(() => categories.map(() => 0));
    for (const e of scoped) {
      const pi = projects.indexOf(e.project);
      const ci = categories.indexOf(e.category);
      if (pi >= 0 && ci >= 0) grid[pi][ci] += e.hours;
    }
    const max = Math.max(...grid.flat(), 0.01);
    return { projects, categories, grid, max };
  });

  let tooltip = $state<{ text: string; x: number; y: number } | null>(null);
</script>

<div class="page">
  <div class="page-header">
    <h1>Charts</h1>
    <div class="date-range">
      <label>
        <span>From</span>
        <input type="date" bind:value={rangeStart} max={rangeEnd} />
      </label>
      <span class="range-sep">→</span>
      <label>
        <span>To</span>
        <input type="date" bind:value={rangeEnd} min={rangeStart} max={todayStr} />
      </label>
    </div>
  </div>

  {#if loadError}
    <p class="error">Could not load entries — is <code>tlserve</code> running?</p>
  {:else if loading}
    <p class="muted">Loading…</p>
  {:else}
    <!-- Donuts -->
    <div class="charts-row">
      <div class="chart-card">
        <h2>Hours by Project</h2>
        {#if projectDonut.segs.length === 0}
          <p class="empty">No data in range</p>
        {:else}
          <div class="donut-wrap">
            <svg viewBox="0 0 200 200" class="donut-svg">
              {#each projectDonut.segs as seg}
                <path
                  d={seg.path} fill={seg.color} opacity="0.9"
                  class="donut-seg"
                  onmouseenter={(e) => tooltip = { text: `${seg.name}: ${seg.hours.toFixed(1)}h (${seg.pct}%)`, x: e.clientX + 12, y: e.clientY - 36 }}
                  onmouseleave={() => tooltip = null}
                />
              {/each}
              <text x="100" y="97" text-anchor="middle" class="donut-big">{projectDonut.total.toFixed(0)}h</text>
              <text x="100" y="114" text-anchor="middle" class="donut-small">total</text>
            </svg>
            <ul class="donut-legend">
              {#each projectDonut.segs as seg}
                <li>
                  <span class="dot" style="background:{seg.color}"></span>
                  <span class="leg-name">{seg.name}</span>
                  <span class="leg-val">{seg.hours.toFixed(1)}h</span>
                  <span class="leg-pct">{seg.pct}%</span>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>

      <div class="chart-card">
        <h2>Hours by Category</h2>
        {#if categoryDonut.segs.length === 0}
          <p class="empty">No data in range</p>
        {:else}
          <div class="donut-wrap">
            <svg viewBox="0 0 200 200" class="donut-svg">
              {#each categoryDonut.segs as seg}
                <path
                  d={seg.path} fill={seg.color} opacity="0.9"
                  class="donut-seg"
                  onmouseenter={(e) => tooltip = { text: `${seg.name}: ${seg.hours.toFixed(1)}h (${seg.pct}%)`, x: e.clientX + 12, y: e.clientY - 36 }}
                  onmouseleave={() => tooltip = null}
                />
              {/each}
              <text x="100" y="97" text-anchor="middle" class="donut-big">{categoryDonut.total.toFixed(0)}h</text>
              <text x="100" y="114" text-anchor="middle" class="donut-small">total</text>
            </svg>
            <ul class="donut-legend">
              {#each categoryDonut.segs as seg}
                <li>
                  <span class="dot" style="background:{seg.color}"></span>
                  <span class="leg-name">{seg.name}</span>
                  <span class="leg-val">{seg.hours.toFixed(1)}h</span>
                  <span class="leg-pct">{seg.pct}%</span>
                </li>
              {/each}
            </ul>
          </div>
        {/if}
      </div>
    </div>

    <!-- Stacked bar -->
    <div class="chart-card">
      <h2>Daily Hours <span class="sub">last 14 days</span></h2>
      <svg viewBox="0 0 {B_SVG_W} {B_SVG_H}" style="width:100%;display:block">
        {#each [0, 0.5, 1] as frac}
          {@const gy = BP_T + BAR_H * (1 - frac)}
          <line x1={BP_L} y1={gy} x2={BP_L + BAR_DAYS * BAR_STEP - 6} y2={gy} class="grid-line" />
          <text x={BP_L - 4} y={gy + 4} text-anchor="end" class="axis-label">{(stackedData.maxH * frac).toFixed(0)}h</text>
        {/each}
        {#each stackedData.bars as bar, di}
          {#if bar.segs.length === 0}
            <rect x={bar.x} y={BP_T + BAR_H - 2} width={BAR_W} height={2} fill="var(--surface2)" rx="1" />
          {:else}
            {#each bar.segs as seg}
              <rect
                x={bar.x} y={seg.y} width={BAR_W} height={seg.segH}
                fill={seg.color} rx="1"
                onmouseenter={(e) => tooltip = { text: `${bar.date} · ${seg.p}: ${seg.h.toFixed(1)}h`, x: e.clientX + 12, y: e.clientY - 36 }}
                onmouseleave={() => tooltip = null}
                style="cursor:pointer"
              />
            {/each}
          {/if}
          {#if di % 2 === 0 || di === BAR_DAYS - 1}
            <text x={bar.x + BAR_W / 2} y={BP_T + BAR_H + 18} text-anchor="middle" class="axis-label">
              {bar.date.slice(5)}
            </text>
          {/if}
        {/each}
      </svg>
      {#if stackedData.allProjects.length > 0}
        <div class="bar-legend">
          {#each stackedData.allProjects as p, i}
            <span class="bar-leg-item"><span class="dot" style="background:{pc(i)}"></span>{p}</span>
          {/each}
        </div>
      {/if}
    </div>

    <!-- Pace line -->
    <div class="chart-card">
      <h2>Daily Pace <span class="sub">last 28 days · dashed = 8h goal</span></h2>
      <svg viewBox="0 0 {L_SVG_W} {L_SVG_H}" style="width:100%;display:block">
        {#each [0, 0.5, 1] as frac}
          {@const ly = LP_T + LC_H * (1 - frac)}
          <line x1={LP_L} y1={ly} x2={LP_L + LC_W} y2={ly} class="grid-line" />
          <text x={LP_L - 4} y={ly + 4} text-anchor="end" class="axis-label">{(paceData.maxH * frac).toFixed(0)}h</text>
        {/each}
        <line
          x1={LP_L} y1={paceData.goalY}
          x2={LP_L + LC_W} y2={paceData.goalY}
          stroke="var(--warning)" stroke-width="1.5" stroke-dasharray="5 3" opacity="0.7"
        />
        <path d={paceData.areaD} fill="var(--accent)" opacity="0.08" />
        <polyline
          points={paceData.polyline}
          fill="none" stroke="var(--accent)" stroke-width="2"
          stroke-linecap="round" stroke-linejoin="round"
        />
        {#each paceData.pts as pt}
          <g
            onmouseenter={(e) => tooltip = { text: `${pt.date} — ${pt.hours.toFixed(1)}h`, x: e.clientX + 12, y: e.clientY - 36 }}
            onmouseleave={() => tooltip = null}
            style="cursor:pointer"
          >
            <circle cx={pt.x} cy={pt.y} r="10" fill="transparent" />
            <circle cx={pt.x} cy={pt.y} r="3" fill="var(--accent)" class="pace-dot" />
          </g>
        {/each}
        {#each paceData.xLabels as lbl}
          <text x={lbl.x} y={LP_T + LC_H + 18} text-anchor="middle" class="axis-label">{lbl.label}</text>
        {/each}
      </svg>
    </div>

    <!-- Project × Category matrix -->
    <div class="chart-card">
      <h2>Project × Category <span class="sub">hours in range</span></h2>
      {#if pcMatrix.projects.length === 0}
        <p class="empty">No data in range</p>
      {:else}
        <div class="matrix-scroll">
          <table class="matrix">
            <thead>
              <tr>
                <th></th>
                {#each pcMatrix.categories as cat}<th class="mh">{cat}</th>{/each}
              </tr>
            </thead>
            <tbody>
              {#each pcMatrix.projects as proj, pi}
                <tr>
                  <td class="ml">{proj}</td>
                  {#each pcMatrix.categories as _cat, ci}
                    {@const h = pcMatrix.grid[pi][ci]}
                    {@const pct = Math.round((h / pcMatrix.max) * 80)}
                    <td
                      class="mc"
                      style="background: color-mix(in srgb, var(--accent) {pct}%, var(--surface2))"
                      onmouseenter={(e) => tooltip = { text: `${proj} × ${pcMatrix.categories[ci]}: ${h.toFixed(1)}h`, x: e.clientX + 12, y: e.clientY - 36 }}
                      onmouseleave={() => tooltip = null}
                    >
                      {#if h > 0}
                        <span class="mv" style="color:{pct > 45 ? 'var(--bg)' : 'var(--text-muted-mid)'}">{h.toFixed(0)}h</span>
                      {/if}
                    </td>
                  {/each}
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </div>
  {/if}
</div>

{#if tooltip}
  <div class="tooltip" style="left:{tooltip.x}px;top:{tooltip.y}px">{tooltip.text}</div>
{/if}

<style>
  .page {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  h1 {
    font-size: 1.6rem;
    font-weight: 700;
    letter-spacing: -0.03em;
  }

  h2 {
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 1rem;
  }

  .sub {
    font-size: 0.8rem;
    font-weight: 400;
    color: var(--text-muted);
  }

  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .date-range {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.85rem;
  }

  .date-range label {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    color: var(--text-muted);
  }

  .date-range input[type='date'] {
    background: var(--surface);
    border: 1px solid var(--border);
    color: var(--text);
    padding: 0.3rem 0.5rem;
    border-radius: 6px;
    font-size: 0.82rem;
    outline: none;
    cursor: pointer;
  }

  .date-range input[type='date']:focus { border-color: var(--accent); }

  .range-sep { color: var(--text-muted); }

  .charts-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
  }

  .chart-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
  }

  /* Donut */
  .donut-wrap {
    display: flex;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .donut-svg {
    width: 160px;
    height: 160px;
    flex-shrink: 0;
  }

  .donut-seg {
    cursor: pointer;
    transition: opacity 0.15s;
  }

  .donut-seg:hover { opacity: 0.7; }

  .donut-big {
    font-size: 28px;
    font-weight: 700;
    fill: var(--text);
    font-family: inherit;
  }

  .donut-small {
    font-size: 11px;
    fill: var(--text-muted);
    font-family: inherit;
  }

  .donut-legend {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
    padding-top: 0.25rem;
    flex: 1;
    min-width: 0;
  }

  .donut-legend li {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.83rem;
  }

  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
  }

  .leg-name {
    color: var(--text-secondary);
    flex: 1;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .leg-val {
    color: var(--text-muted-mid);
    font-variant-numeric: tabular-nums;
    font-size: 0.8rem;
  }

  .leg-pct {
    color: var(--text-muted);
    font-size: 0.75rem;
    width: 2.5rem;
    text-align: right;
    font-variant-numeric: tabular-nums;
  }

  /* SVG shared */
  .grid-line {
    stroke: var(--border-subtle);
    stroke-width: 0.5;
  }

  .axis-label {
    font-size: 9px;
    fill: var(--text-muted);
    font-family: inherit;
  }

  /* Stacked bar legend */
  .bar-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;
    margin-top: 0.75rem;
  }

  .bar-leg-item {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    font-size: 0.8rem;
    color: var(--text-muted-mid);
  }

  /* Pace line dots */
  .pace-dot {
    opacity: 0.25;
    transition: opacity 0.1s;
  }

  g:hover .pace-dot { opacity: 1; }

  /* Matrix */
  .matrix-scroll { overflow-x: auto; }

  .matrix { border-collapse: collapse; font-size: 0.82rem; }

  .matrix th,
  .matrix td { padding: 0; }

  .mh {
    color: var(--text-muted);
    font-weight: 500;
    text-align: center;
    padding: 0 0.4rem 0.5rem;
    font-size: 0.78rem;
    white-space: nowrap;
  }

  .ml {
    color: var(--text-secondary);
    font-weight: 500;
    padding: 0.3rem 1rem 0.3rem 0;
    white-space: nowrap;
    font-size: 0.85rem;
  }

  .mc {
    width: 72px;
    height: 38px;
    text-align: center;
    border-radius: 4px;
    border: 2px solid var(--surface);
    transition: opacity 0.15s;
    cursor: default;
  }

  .mc:hover { opacity: 0.8; cursor: pointer; }

  .mv {
    font-size: 0.78rem;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }

  /* Tooltip */
  .tooltip {
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

  /* Utility */
  .muted { color: var(--text-muted); }
  .empty { color: var(--text-muted); font-size: 0.9rem; }
  .error { color: var(--error); font-size: 0.9rem; }

  code {
    background: var(--surface2);
    padding: 0.1em 0.4em;
    border-radius: 4px;
    font-size: 0.85em;
  }

  @media (max-width: 700px) {
    .charts-row { grid-template-columns: 1fr; }
    .donut-wrap { flex-direction: column; align-items: center; }
  }
</style>
