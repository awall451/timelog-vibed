<script lang="ts">
  const features = [
    { icon: '🔥', title: 'GitHub-style heatmap', body: 'See your year of work at a glance — daily intensity, filterable by project or category.' },
    { icon: '📊', title: 'Charts & analytics', body: 'Donut breakdowns, daily stacked bars, weekly pace lines — pure SVG, no chart library.' },
    { icon: '⏱️', title: 'Live timer', body: 'Start a timer in the corner widget; stop to pre-fill the log form. Survives refresh.' },
    { icon: '🎨', title: 'Six themes', body: 'Default dark, Tokyo Night, Cyberpunk, Dracula, Rose Pine, Catppuccin — instant switch.' },
    { icon: '📦', title: 'CSV import / export', body: 'Bring your old data in, take it back out. Plain CSV, no lock-in.' },
    { icon: '💾', title: 'Local-first', body: 'SQLite on disk. Your time data never leaves your machine.' },
  ];
</script>

<div class="landing">
  <section class="hero">
    <div class="demo-banner">Live demo · data is local to your browser</div>
    <h1>Timelog</h1>
    <p class="tagline">A local-first time tracker built for developers.</p>
    <div class="cta-row">
      <a href="/dashboard" class="cta-primary">Try the demo →</a>
      <a href="https://github.com/awall451/timelog-vibed" class="cta-secondary" target="_blank" rel="noopener">View on GitHub</a>
    </div>
  </section>

  <section class="video-section">
    <div class="video-frame">
      <video
        src="/demo.webm"
        poster="/demo-poster.png"
        autoplay
        muted
        loop
        playsinline
        preload="metadata"
        controls
      ></video>
    </div>
    <p class="video-caption">~30 seconds · log an entry, browse the heatmap, switch themes, and more.</p>
  </section>

  <section class="features">
    <h2>What's inside</h2>
    <div class="grid">
      {#each features as f}
        <div class="card">
          <div class="card-icon">{f.icon}</div>
          <h3>{f.title}</h3>
          <p>{f.body}</p>
        </div>
      {/each}
    </div>
  </section>

  <section class="how">
    <h2>How it works</h2>
    <div class="steps">
      <div class="step">
        <div class="step-num">1</div>
        <div>
          <h3>Log</h3>
          <p>One quick form: project, category, hours, description. Or run the timer.</p>
        </div>
      </div>
      <div class="step">
        <div class="step-num">2</div>
        <div>
          <h3>Review</h3>
          <p>Filter by date, project, or category. Edit and delete inline.</p>
        </div>
      </div>
      <div class="step">
        <div class="step-num">3</div>
        <div>
          <h3>Analyze</h3>
          <p>Heatmap and charts show where your time actually goes.</p>
        </div>
      </div>
    </div>
  </section>

  <section class="footer-cta">
    <a href="/dashboard" class="cta-primary">Try the demo →</a>
    <p class="reset-note">Want a clean slate? Settings → Data → "Reset demo data".</p>
  </section>
</div>

<style>
  .landing {
    display: flex;
    flex-direction: column;
    gap: 4rem;
    padding-bottom: 3rem;
  }

  /* Hero */
  .hero {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 1rem;
    padding-top: 2rem;
  }

  .demo-banner {
    background: var(--surface2);
    color: var(--text-muted-mid);
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-size: 0.78rem;
    letter-spacing: 0.04em;
    border: 1px solid var(--border);
  }

  .hero h1 {
    font-size: clamp(2.5rem, 6vw, 4rem);
    font-weight: 800;
    letter-spacing: -0.04em;
    background: linear-gradient(135deg, var(--accent), var(--accent-light));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .tagline {
    font-size: 1.15rem;
    color: var(--text-secondary);
    max-width: 36rem;
  }

  .cta-row {
    display: flex;
    gap: 0.85rem;
    margin-top: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
  }

  .cta-primary {
    background: var(--accent);
    color: #fff;
    text-decoration: none;
    padding: 0.85rem 1.6rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    transition: background 0.15s, transform 0.1s;
  }

  .cta-primary:hover { background: var(--accent-hover); transform: translateY(-1px); }

  .cta-secondary {
    background: transparent;
    color: var(--text-muted-mid);
    text-decoration: none;
    padding: 0.85rem 1.4rem;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    border: 1px solid var(--border);
    transition: color 0.15s, border-color 0.15s;
  }

  .cta-secondary:hover { color: var(--text); border-color: var(--accent); }

  /* Video */
  .video-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.6rem;
  }

  .video-frame {
    width: 100%;
    max-width: 920px;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: var(--surface);
    box-shadow: 0 20px 60px -20px rgba(0, 0, 0, 0.5);
  }

  .video-frame video {
    display: block;
    width: 100%;
    height: auto;
  }

  .video-caption {
    color: var(--text-muted);
    font-size: 0.85rem;
  }

  /* Features */
  .features h2,
  .how h2 {
    font-size: 1.4rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    text-align: center;
    margin-bottom: 1.5rem;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1rem;
  }

  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    transition: border-color 0.15s, transform 0.1s;
  }

  .card:hover { border-color: var(--accent); transform: translateY(-2px); }

  .card-icon {
    font-size: 1.6rem;
  }

  .card h3 {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text);
  }

  .card p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
  }

  /* How it works */
  .steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 1rem;
  }

  .step {
    display: flex;
    gap: 0.85rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.25rem;
  }

  .step-num {
    flex-shrink: 0;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: var(--accent);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.9rem;
  }

  .step h3 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
  }

  .step p {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
  }

  /* Footer CTA */
  .footer-cta {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.6rem;
    padding: 2rem 0;
    border-top: 1px solid var(--border-subtle);
  }

  .reset-note {
    color: var(--text-muted);
    font-size: 0.85rem;
  }

  @media (max-width: 600px) {
    .landing { gap: 2.5rem; }
    .hero { padding-top: 1rem; }
    .cta-row { width: 100%; flex-direction: column; }
    .cta-primary, .cta-secondary { text-align: center; }
  }
</style>
