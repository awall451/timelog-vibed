<script lang="ts">
  let { children } = $props();
</script>

<div class="app">
  <header>
    <nav>
      <a href="/" class="brand">🕐 Timelog</a>
      <div class="links">
        <a href="/">Dashboard</a>
        <a href="/entries">Entries</a>
        <a href="/log">Log Time</a>
      </div>
    </nav>
  </header>

  <main>
    {@render children()}
  </main>
</div>

<style>
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  :global(body) {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #0f1117;
    color: #e2e8f0;
    min-height: 100vh;
  }

  .app {
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }

  header {
    background: #1a1d27;
    border-bottom: 1px solid #2d3148;
    padding: 0 2rem;
  }

  nav {
    max-width: 1100px;
    margin: 0 auto;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .brand {
    font-size: 1.1rem;
    font-weight: 700;
    color: #e2e8f0;
    text-decoration: none;
    letter-spacing: -0.02em;
  }

  .links {
    display: flex;
    gap: 1.5rem;
  }

  .links a {
    color: #94a3b8;
    text-decoration: none;
    font-size: 0.9rem;
    transition: color 0.15s;
  }

  .links a:hover {
    color: #e2e8f0;
  }

  main {
    flex: 1;
    max-width: 1100px;
    width: 100%;
    margin: 0 auto;
    padding: 2rem;
  }
</style>
