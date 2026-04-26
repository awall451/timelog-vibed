<script lang="ts">
  import { page } from '$app/state';

  let { children } = $props();

  type Item = { label: string; path: string };
  type Group = { label: string; items: Item[] };

  // Tree config — designed to grow into multi-mode without UI changes.
  // When TIMELOG_MODE=multi lands, additional groups (Workspace, Admin) push in here.
  const groups: Group[] = [
    {
      label: 'User',
      items: [
        { label: 'General',         path: '/settings/general' },
        { label: 'Appearance',      path: '/settings/appearance' },
        { label: 'Timer & Behavior', path: '/settings/timer' },
        { label: 'AI Sync',         path: '/settings/ai-sync' },
        { label: 'Data',            path: '/settings/storage' },
      ],
    },
  ];

  let current = $derived(page.url.pathname);
</script>

<div class="settings-shell">
  <aside class="tree" aria-label="Settings categories">
    {#each groups as group (group.label)}
      <div class="tree-group">
        <div class="tree-group-label">{group.label}</div>
        <ul>
          {#each group.items as item (item.path)}
            <li>
              <a
                href={item.path}
                class:active={current === item.path}
              >{item.label}</a>
            </li>
          {/each}
        </ul>
      </div>
    {/each}
  </aside>

  <section class="content">
    {@render children()}
  </section>
</div>

<style>
  .settings-shell {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 1.5rem;
    min-height: calc(100vh - 56px - 4rem);
    align-items: start;
  }

  .tree {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1rem 0.5rem;
    position: sticky;
    top: 1rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .tree-group-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    padding: 0 0.75rem 0.4rem;
    font-weight: 600;
  }

  .tree-group ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.1rem;
  }

  .tree-group li a {
    display: block;
    padding: 0.45rem 0.75rem;
    border-radius: 6px;
    color: var(--text-secondary);
    text-decoration: none;
    font-size: 0.88rem;
    transition: background 0.1s, color 0.1s;
    border-left: 2px solid transparent;
  }

  .tree-group li a:hover {
    background: var(--surface2);
    color: var(--text);
  }

  .tree-group li a.active {
    background: var(--surface2);
    color: var(--accent);
    border-left-color: var(--accent);
    font-weight: 500;
  }

  .content {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.75rem 2rem;
    min-width: 0;
  }

  @media (max-width: 760px) {
    .settings-shell {
      grid-template-columns: 1fr;
    }
    .tree {
      position: static;
    }
  }
</style>
