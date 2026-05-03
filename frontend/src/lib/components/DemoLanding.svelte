<script lang="ts">
  const features = [
    { icon: '🔥', title: 'GitHub-style heatmap', body: 'See your year of work at a glance — daily intensity, filterable by project or category.' },
    { icon: '📊', title: 'Charts & analytics', body: 'Donut breakdowns, daily stacked bars, weekly pace lines — pure SVG, no chart library.' },
    { icon: '⏱️', title: 'Live timer', body: 'Start a timer in the corner widget; stop to pre-fill the log form. Survives refresh.' },
    { icon: '🎨', title: 'Six themes', body: 'Default dark, Tokyo Night, Cyberpunk, Dracula, Rose Pine, Catppuccin — instant switch.' },
    { icon: '📦', title: 'CSV import / export', body: 'Bring your old data in, take it back out. Plain CSV, no lock-in.' },
    { icon: '💾', title: 'Local-first', body: 'SQLite on disk. Your time data never leaves your machine.' },
  ];

  const corePlanned = [
    { title: 'Entry templates', body: 'One-click pre-fill for common project + category combos.' },
    { title: 'Weekly goals', body: 'Per-project hour targets with progress bars on the dashboard.' },
    { title: 'PDF timesheet export', body: 'Grouped by project, date-ranged, browser-rendered.' },
    { title: 'Tags', body: 'Free-form labels for cross-cutting work — filter on anything.' },
    { title: 'PWA + offline log', body: 'Installable on phone. Log time even on the train.' },
    { title: 'AI session sync', body: 'Auto-suggest entries from Claude Code session history.' },
  ];

  const teamFeatures = [
    { icon: '🔐', title: 'OIDC single sign-on', body: 'Dex, Google Workspace, Okta, Auth0 — same code path, one env var.' },
    { icon: '👥', title: 'Roles & approvals', body: 'Admin / manager / member. Submit → approve → lock workflow.' },
    { icon: '💸', title: 'Billing engine', body: 'Hours × rate → invoice PDFs. Per-user or per-project rate cards.' },
    { icon: '📈', title: 'Admin dashboard', body: 'Cross-user utilization, project budgets, hour-cap alerts.' },
    { icon: '💬', title: 'Slack / Teams bot', body: '`/log 2h ProjectX dev` from chat. Entry created.' },
    { icon: '🌐', title: 'Client portal', body: 'Read-only billed-hours view for clients you invoice.' },
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

  <section class="sandbox">
    <div class="sandbox-card">
      <div class="sandbox-icon">🧪</div>
      <div class="sandbox-body">
        <h2>Go nuts — you can't break a thing</h2>
        <p>
          Everything you see here is <strong>fake mock data</strong> running in
          your own browser. Add entries, delete them, change themes, mash buttons
          — it only touches your local copy. Nothing gets sent anywhere, no other
          visitor sees your changes, and there's no "real" account to mess up.
        </p>
        <ul class="sandbox-points">
          <li><span class="dot">●</span> <strong>Mock data only</strong> — none of these projects, hours, or entries are real.</li>
          <li><span class="dot">●</span> <strong>Just for you</strong> — every visitor gets their own private copy in their browser. Your changes never reach anyone else.</li>
          <li><span class="dot">●</span> <strong>Wipe it whenever</strong> — Settings → Data → "Reset demo data" puts everything back to a clean slate in one click.</li>
        </ul>
        <p class="sandbox-foot">
          Seriously — click around, experiment, try every button. The worst thing
          that can happen is you reload the page.
        </p>
      </div>
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

  <section class="roadmap">
    <div class="roadmap-header">
      <h2>What's next</h2>
      <div class="badge-strip">
        <span class="rb">MIT forever</span>
        <span class="rb">One repo</span>
        <span class="rb">Free for personal &amp; team</span>
      </div>
    </div>

    <div class="roadmap-grid">
      <div class="track">
        <div class="track-head">
          <span class="track-tag core">Personal app</span>
          <h3>Coming soon</h3>
        </div>
        <ul class="checklist">
          {#each corePlanned as p}
            <li>
              <span class="check">▸</span>
              <div>
                <strong>{p.title}</strong>
                <p>{p.body}</p>
              </div>
            </li>
          {/each}
        </ul>
      </div>

      <div class="track">
        <div class="track-head">
          <span class="track-tag team">Team mode</span>
          <h3>The team future</h3>
        </div>
        <p class="track-intro">
          Same codebase. Opt in with one env var (<code>TIMELOG_MODE=multi</code>).
          Personal users never see the team code; teams get a real multi-user app.
        </p>
        <div class="team-grid">
          {#each teamFeatures as f}
            <div class="team-card">
              <div class="team-icon">{f.icon}</div>
              <h4>{f.title}</h4>
              <p>{f.body}</p>
            </div>
          {/each}
        </div>
      </div>
    </div>

    <p class="roadmap-foot">
      No closed-source split. No "open core" trick. The team edition ships in the
      same MIT repo as the personal app — every line of it. If hosted SaaS ever
      happens, the code stays free.
    </p>
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

  /* Sandbox reassurance */
  .sandbox {
    display: flex;
    justify-content: center;
  }

  .sandbox-card {
    width: 100%;
    max-width: 920px;
    background: linear-gradient(135deg, var(--surface), var(--surface2));
    border: 1px solid var(--accent);
    border-radius: 12px;
    padding: 1.5rem 1.75rem;
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 1.25rem;
    align-items: start;
    box-shadow: 0 0 0 1px var(--accent-light) inset;
  }

  .sandbox-icon {
    font-size: 2.5rem;
    line-height: 1;
    padding-top: 0.15rem;
  }

  .sandbox-body h2 {
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    margin-bottom: 0.5rem;
    color: var(--text);
  }

  .sandbox-body > p {
    color: var(--text-secondary);
    font-size: 0.95rem;
    line-height: 1.55;
  }

  .sandbox-body strong { color: var(--text); }

  .sandbox-points {
    list-style: none;
    padding: 0;
    margin: 0.85rem 0 0;
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
  }

  .sandbox-points li {
    color: var(--text-secondary);
    font-size: 0.88rem;
    line-height: 1.5;
    display: grid;
    grid-template-columns: 1rem 1fr;
    gap: 0.5rem;
    align-items: baseline;
  }

  .sandbox-points .dot {
    color: var(--accent);
    font-size: 0.6rem;
  }

  .sandbox-foot {
    margin-top: 0.85rem;
    color: var(--text-muted);
    font-size: 0.85rem;
    font-style: italic;
  }

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

  /* Roadmap */
  .roadmap {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }

  .roadmap-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.85rem;
    text-align: center;
  }

  .badge-strip {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
  }

  .rb {
    background: var(--surface2);
    color: var(--accent-light);
    border: 1px solid var(--border);
    padding: 0.3rem 0.75rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.02em;
  }

  .roadmap-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1.4fr);
    gap: 1.5rem;
  }

  .track {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .track-head {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .track-head h3 {
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text);
  }

  .track-tag {
    align-self: flex-start;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }

  .track-tag.core {
    background: var(--surface2);
    color: var(--accent-light);
    border: 1px solid var(--accent);
  }

  .track-tag.team {
    background: var(--accent);
    color: #fff;
    border: 1px solid var(--accent);
  }

  .checklist {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .checklist li {
    display: grid;
    grid-template-columns: 1.2rem 1fr;
    gap: 0.6rem;
    align-items: start;
  }

  .check {
    color: var(--accent);
    font-weight: 700;
    line-height: 1.4;
  }

  .checklist strong {
    color: var(--text);
    font-size: 0.95rem;
    display: block;
    margin-bottom: 0.15rem;
  }

  .checklist p {
    color: var(--text-secondary);
    font-size: 0.85rem;
    line-height: 1.45;
  }

  .track-intro {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.55;
  }

  .track-intro code {
    background: var(--surface2);
    color: var(--accent-light);
    padding: 0.1em 0.4em;
    border-radius: 4px;
    font-size: 0.85em;
  }

  .team-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.75rem;
  }

  .team-card {
    background: var(--surface2);
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    padding: 0.85rem;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    transition: border-color 0.15s;
  }

  .team-card:hover { border-color: var(--accent); }

  .team-icon { font-size: 1.25rem; }

  .team-card h4 {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text);
  }

  .team-card p {
    color: var(--text-secondary);
    font-size: 0.8rem;
    line-height: 1.45;
  }

  .roadmap-foot {
    text-align: center;
    color: var(--text-muted);
    font-size: 0.88rem;
    line-height: 1.55;
    max-width: 42rem;
    margin: 0 auto;
    font-style: italic;
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

  @media (max-width: 800px) {
    .roadmap-grid { grid-template-columns: minmax(0, 1fr); }
  }

  @media (max-width: 600px) {
    .landing { gap: 2.5rem; }
    .hero { padding-top: 1rem; }
    .cta-row { width: 100%; flex-direction: column; }
    .cta-primary, .cta-secondary { text-align: center; }
    .sandbox-card { grid-template-columns: 1fr; gap: 0.85rem; padding: 1.25rem; }
    .sandbox-icon { font-size: 2rem; }
  }
</style>
