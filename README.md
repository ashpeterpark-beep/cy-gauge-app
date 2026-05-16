<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>cy-gauge-app — Discrete Calabi–Yau Gauge Functor Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet"/>
<style>
  :root {
    --bg: #060810;
    --surface: #0c0f1a;
    --border: rgba(78,232,208,0.12);
    --teal: #4ee8d0;
    --orange: #f97316;
    --purple: #c084fc;
    --yellow: #facc15;
    --text: #e2e8f0;
    --muted: rgba(226,232,240,0.4);
    --dim: rgba(226,232,240,0.15);
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', sans-serif;
    overflow-x: hidden;
    line-height: 1.6;
  }

  /* ── HERO ── */
  #hero {
    position: relative;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    padding: 60px 20px;
  }

  #hero-canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
  }

  .hero-content {
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 800px;
  }

  .hero-eyebrow {
    font-family: 'Space Mono', monospace;
    font-size: 10px;
    letter-spacing: 5px;
    color: var(--teal);
    margin-bottom: 18px;
    text-transform: uppercase;
  }

  .hero-title {
    font-family: 'Orbitron', monospace;
    font-size: clamp(28px, 5vw, 56px);
    font-weight: 900;
    line-height: 1.1;
    color: #fff;
    text-shadow: 0 0 60px rgba(78,232,208,0.3);
    margin-bottom: 10px;
  }

  .hero-title span { color: var(--teal); }

  .hero-subtitle {
    font-size: 16px;
    color: var(--muted);
    margin-bottom: 36px;
    font-weight: 300;
    letter-spacing: 0.5px;
  }

  .badges {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-bottom: 40px;
  }

  .badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.04);
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 1px;
    color: var(--muted);
    backdrop-filter: blur(4px);
  }
  .badge .dot { width: 6px; height: 6px; border-radius: 50%; }
  .badge.teal .dot { background: var(--teal); }
  .badge.orange .dot { background: var(--orange); }
  .badge.purple .dot { background: var(--purple); }
  .badge.yellow .dot { background: var(--yellow); }

  .hero-btns { display: flex; gap: 12px; justify-content: center; }
  .btn-primary {
    padding: 12px 28px;
    background: rgba(78,232,208,0.15);
    border: 1px solid var(--teal);
    color: var(--teal);
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: background 0.2s;
    text-transform: uppercase;
  }
  .btn-primary:hover { background: rgba(78,232,208,0.25); }
  .btn-secondary {
    padding: 12px 28px;
    background: transparent;
    border: 1px solid rgba(255,255,255,0.15);
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    cursor: pointer;
    text-decoration: none;
    display: inline-block;
    transition: border-color 0.2s;
    text-transform: uppercase;
  }
  .btn-secondary:hover { border-color: rgba(255,255,255,0.35); }

  .scroll-hint {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 3px;
    color: var(--dim);
    animation: pulse 2s infinite;
    z-index: 2;
  }

  /* ── SECTION LAYOUT ── */
  section {
    padding: 80px 24px;
    max-width: 1100px;
    margin: 0 auto;
  }

  .section-label {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 5px;
    color: var(--teal);
    margin-bottom: 12px;
    text-transform: uppercase;
  }

  h2 {
    font-family: 'Orbitron', monospace;
    font-size: clamp(20px, 3vw, 30px);
    font-weight: 700;
    color: #fff;
    margin-bottom: 32px;
  }

  h3 {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: var(--teal);
    margin-bottom: 14px;
    letter-spacing: 1px;
  }

  p { color: var(--muted); margin-bottom: 16px; font-size: 14px; }

  .divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(78,232,208,0.2), transparent);
    margin: 0;
  }

  /* ── APP PREVIEW ── */
  .app-preview-container {
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    overflow: hidden;
    margin-top: 20px;
  }

  /* Fake browser chrome */
  .browser-chrome {
    background: #0a0d18;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 10px 14px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .browser-dots { display: flex; gap: 6px; }
  .browser-dots span {
    width: 10px; height: 10px; border-radius: 50%;
    background: rgba(255,255,255,0.12);
  }
  .browser-url {
    flex: 1;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 4px 12px;
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: var(--dim);
    letter-spacing: 1px;
  }

  .app-inner {
    display: flex;
    height: 460px;
  }

  /* Fake sidebar */
  .fake-sidebar {
    width: 220px;
    min-width: 220px;
    background: rgba(255,255,255,0.015);
    border-right: 1px solid rgba(255,255,255,0.05);
    padding: 16px 12px;
    overflow: hidden;
  }

  .fake-label {
    font-family: 'Space Mono', monospace;
    font-size: 7px;
    letter-spacing: 3px;
    color: var(--teal);
    margin-bottom: 12px;
  }

  .fake-slider-group { margin-bottom: 18px; }
  .fake-slider-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    color: var(--dim);
    margin-bottom: 5px;
  }
  .fake-slider-track {
    height: 2px;
    background: rgba(255,255,255,0.07);
    position: relative;
    margin-bottom: 10px;
  }
  .fake-slider-fill {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    background: var(--teal);
  }
  .fake-slider-fill.orange { background: var(--orange); }
  .fake-slider-fill.purple { background: var(--purple); }

  .fake-run-btn {
    width: 100%;
    padding: 8px;
    background: rgba(78,232,208,0.12);
    border: 1px solid rgba(78,232,208,0.3);
    color: var(--teal);
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 2px;
    text-align: center;
    margin-top: auto;
  }

  /* Fake main area */
  .fake-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }

  .fake-stat-row {
    display: flex;
    gap: 8px;
    padding: 10px 14px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    flex-wrap: wrap;
  }

  .fake-stat {
    padding: 6px 12px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
  }
  .fake-stat-label {
    font-family: 'Space Mono', monospace;
    font-size: 6px;
    letter-spacing: 2px;
    color: var(--dim);
    margin-bottom: 2px;
  }
  .fake-stat-val {
    font-family: 'Space Mono', monospace;
    font-size: 13px;
    color: var(--teal);
  }
  .fake-stat-val.orange { color: var(--orange); }
  .fake-stat-val.purple { color: var(--purple); }

  .fake-tabs {
    display: flex;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    padding: 0 14px;
  }
  .fake-tab {
    padding: 8px 14px;
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 2px;
    color: var(--dim);
    border-bottom: 2px solid transparent;
  }
  .fake-tab.active {
    color: var(--teal);
    border-bottom-color: var(--teal);
  }

  .fake-canvas-area {
    flex: 1;
    position: relative;
    overflow: hidden;
    background: rgba(255,255,255,0.01);
    margin: 12px;
    border: 1px solid rgba(255,255,255,0.05);
  }

  #ui-canvas { width: 100%; height: 100%; }

  /* ── MATH DIAGRAM SECTION ── */
  .math-diagram-wrapper {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-top: 20px;
  }

  @media (max-width: 700px) { .math-diagram-wrapper { grid-template-columns: 1fr; } }

  .diagram-card {
    background: var(--surface);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 0;
    overflow: hidden;
  }

  .diagram-card-header {
    padding: 12px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 3px;
    color: var(--teal);
  }

  .diagram-card canvas { display: block; width: 100%; }

  /* ── ARCHITECTURE ── */
  .arch-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 20px;
  }
  @media (max-width: 700px) { .arch-grid { grid-template-columns: 1fr; } }

  .arch-card {
    background: var(--surface);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 20px;
  }

  .arch-card h3 { color: var(--teal); margin-bottom: 12px; }

  .file-tree {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    line-height: 2.0;
    color: var(--muted);
  }
  .file-tree .root { color: var(--teal); }
  .file-tree .py { color: #60a5fa; }
  .file-tree .jsx { color: #34d399; }
  .file-tree .cfg { color: var(--orange); }
  .file-tree .comment { color: var(--dim); }

  /* ── API TABLE ── */
  .api-section { margin-top: 20px; }
  .api-endpoint {
    border: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 16px;
    overflow: hidden;
  }
  .api-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 16px;
    background: rgba(255,255,255,0.03);
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }
  .api-method {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    padding: 3px 10px;
    font-weight: 700;
  }
  .api-method.post { background: rgba(249,115,22,0.15); color: var(--orange); border: 1px solid rgba(249,115,22,0.3); }
  .api-method.get  { background: rgba(78,232,208,0.10); color: var(--teal);   border: 1px solid rgba(78,232,208,0.3); }
  .api-path {
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: var(--text);
  }
  .api-desc { font-size: 12px; color: var(--dim); margin-left: auto; }
  .api-body { padding: 16px; }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    margin-bottom: 0;
  }
  thead th {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 2px;
    color: var(--dim);
    text-align: left;
    padding: 6px 12px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.02);
  }
  tbody td {
    padding: 8px 12px;
    border-bottom: 1px solid rgba(255,255,255,0.03);
    color: var(--muted);
    vertical-align: top;
  }
  tbody td:first-child {
    font-family: 'Space Mono', monospace;
    font-size: 11px;
    color: var(--teal);
  }
  tbody tr:last-child td { border-bottom: none; }

  /* ── PIPELINE DIAGRAM ── */
  #pipeline-canvas { display: block; width: 100%; }

  /* ── QUICK START ── */
  .code-block {
    background: #050710;
    border: 1px solid rgba(255,255,255,0.06);
    padding: 20px 24px;
    font-family: 'Space Mono', monospace;
    font-size: 12px;
    color: #a5f3fc;
    overflow-x: auto;
    margin: 12px 0;
    line-height: 2;
    position: relative;
  }
  .code-block .comment { color: var(--dim); }
  .code-block .cmd { color: #86efac; }
  .code-block .url { color: var(--orange); }
  .code-label {
    font-family: 'Space Mono', monospace;
    font-size: 8px;
    letter-spacing: 3px;
    color: var(--dim);
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-bottom: none;
    padding: 6px 14px;
    display: inline-block;
  }

  .quick-start-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-top: 20px;
  }
  @media (max-width: 700px) { .quick-start-grid { grid-template-columns: 1fr; } }

  .qs-card {
    background: var(--surface);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 20px;
  }
  .qs-card h3 { font-size: 11px; margin-bottom: 14px; }

  /* ── FOOTER ── */
  footer {
    border-top: 1px solid rgba(78,232,208,0.1);
    padding: 40px 24px;
    text-align: center;
  }
  .footer-title {
    font-family: 'Orbitron', monospace;
    font-size: 16px;
    color: var(--teal);
    margin-bottom: 8px;
  }
  .footer-sub {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 3px;
    color: var(--dim);
    margin-bottom: 24px;
  }
  .footer-links { display: flex; gap: 20px; justify-content: center; }
  .footer-links a {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: var(--dim);
    text-decoration: none;
    text-transform: uppercase;
    transition: color 0.2s;
  }
  .footer-links a:hover { color: var(--teal); }

  @keyframes pulse { 0%,100%{opacity:0.3} 50%{opacity:0.7} }
  @keyframes fadeInUp { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }

  .hero-content > * {
    animation: fadeInUp 0.8s ease both;
  }
  .hero-content > *:nth-child(1){animation-delay:0.1s}
  .hero-content > *:nth-child(2){animation-delay:0.2s}
  .hero-content > *:nth-child(3){animation-delay:0.3s}
  .hero-content > *:nth-child(4){animation-delay:0.4s}
  .hero-content > *:nth-child(5){animation-delay:0.5s}

  /* TOC */
  nav.toc {
    background: var(--surface);
    border: 1px solid var(--border);
    padding: 20px 24px;
    max-width: 1100px;
    margin: 0 auto;
    display: flex;
    flex-wrap: wrap;
    gap: 6px 24px;
  }
  nav.toc a {
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    color: var(--dim);
    text-decoration: none;
    transition: color 0.2s;
    text-transform: uppercase;
  }
  nav.toc a:hover { color: var(--teal); }
  nav.toc a::before { content: "›  "; color: var(--teal); }

  /* Glows */
  .glow-teal { color: var(--teal); text-shadow: 0 0 20px rgba(78,232,208,0.5); }
  .tag {
    display: inline-block;
    padding: 2px 8px;
    background: rgba(78,232,208,0.08);
    border: 1px solid rgba(78,232,208,0.2);
    font-family: 'Space Mono', monospace;
    font-size: 9px;
    color: var(--teal);
    letter-spacing: 1px;
  }
  .tag.orange { background: rgba(249,115,22,0.08); border-color: rgba(249,115,22,0.2); color: var(--orange); }
  .tag.purple { background: rgba(192,132,252,0.08); border-color: rgba(192,132,252,0.2); color: var(--purple); }

  /* Number */
  .step-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-top: 24px;
  }
  .step-card {
    background: var(--surface);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 20px;
    position: relative;
  }
  .step-number {
    font-family: 'Orbitron', monospace;
    font-size: 36px;
    font-weight: 900;
    color: rgba(78,232,208,0.08);
    position: absolute;
    top: 10px;
    right: 14px;
    line-height: 1;
  }
  .step-card h3 { font-size: 10px; letter-spacing: 2px; margin-bottom: 8px; }
  .step-card p { font-size: 12px; }
</style>
</head>
<body>

<!-- ═══════════════════════════════════════════ HERO ═══ -->
<section id="hero">
  <canvas id="hero-canvas"></canvas>

  <div class="hero-content">
    <div class="hero-eyebrow">ashpeterpark-beep / cy-gauge-app</div>
    <h1 class="hero-title">Discrete Calabi–Yau<br/><span>Gauge Functor</span> Dashboard</h1>
    <p class="hero-subtitle">Full-stack lattice gauge theory visualisation · FastAPI + React + SciPy</p>

    <div class="badges">
      <div class="badge teal"><div class="dot"></div>MIT License</div>
      <div class="badge teal"><div class="dot"></div>FastAPI 0.115</div>
      <div class="badge teal"><div class="dot"></div>React 18 + Vite</div>
      <div class="badge orange"><div class="dot"></div>Python 3.10+</div>
      <div class="badge orange"><div class="dot"></div>NumPy · SciPy</div>
      <div class="badge purple"><div class="dot"></div>Docker Ready</div>
      <div class="badge purple"><div class="dot"></div>Sparse eigsh</div>
    </div>

    <div class="hero-btns">
      <a class="btn-primary" href="https://github.com/ashpeterpark-beep/cy-gauge-app" target="_blank">View on GitHub</a>
      <a class="btn-secondary" href="#quick-start">Quick Start ↓</a>
    </div>
  </div>

  <div class="scroll-hint">SCROLL TO EXPLORE</div>
</section>

<div class="divider"></div>

<!-- TOC -->
<nav class="toc">
  <a href="#overview">Overview</a>
  <a href="#preview">App Preview</a>
  <a href="#math">Mathematics</a>
  <a href="#architecture">Architecture</a>
  <a href="#tabs">Dashboard Tabs</a>
  <a href="#api">API Reference</a>
  <a href="#quick-start">Quick Start</a>
  <a href="#deploy">Deployment</a>
</nav>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ OVERVIEW ═══ -->
<section id="overview">
  <div class="section-label">01 · Overview</div>
  <h2>What is cy-gauge-app?</h2>
  <p>
    <strong style="color:var(--text)">cy-gauge-app</strong> is a full-stack web application that brings
    the mathematics of discrete Calabi–Yau geometry to life. It runs a complete
    <span class="tag">U(N) lattice gauge theory</span> pipeline over a 4-dimensional torus
    (approximating a Calabi–Yau manifold), exposing every step as a live,
    interactive visualisation inside a browser.
  </p>
  <p>
    The <span class="tag orange">FastAPI</span> backend executes real <code style="color:var(--teal)">numpy</code>/<code style="color:var(--teal)">scipy</code>
    numerical code: mesh construction, random SU(N) link generation, curvature computation,
    slope filtration, wall-crossing sweeps, and sparse Dolbeault Laplacian eigensolving.
    The <span class="tag">React + Vite</span> frontend visualises results interactively on raw HTML5 <code style="color:var(--teal)">&lt;canvas&gt;</code> elements.
  </p>

  <div class="step-grid">
    <div class="step-card">
      <div class="step-number">01</div>
      <h3>Lattice Mesh</h3>
      <p>Builds a discrete T⁴ simplicial complex with configurable grid density per axis. Vertices, edges, and triangular faces are extracted with periodic boundary conditions.</p>
    </div>
    <div class="step-card">
      <div class="step-number">02</div>
      <h3>Gauge Field</h3>
      <p>Random SU(N) link variables U<sub>e</sub> = exp(iεH<sub>e</sub>) are generated for each edge using matrix exponentiation from scipy.</p>
    </div>
    <div class="step-card">
      <div class="step-number">03</div>
      <h3>Curvature & Slopes</h3>
      <p>Face holonomies compute the curvature 2-form F<sub>f</sub>. The Hermitian endomorphism Φ yields slope eigenvalues λ₁ ≥ λ₂ via the Harder–Narasimhan filtration.</p>
    </div>
    <div class="step-card">
      <div class="step-number">04</div>
      <h3>Dolbeault Spectrum</h3>
      <p>A sparse FEEC Dolbeault operator ∂̄ is assembled and its Laplacian Δ = ∂̄†∂̄ diagonalised via shift-invert eigsh, counting zero modes (harmonic forms).</p>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ APP PREVIEW ═══ -->
<section id="preview">
  <div class="section-label">02 · App Preview</div>
  <h2>What you see when you open it</h2>
  <p>The dashboard opens to a dark, monospace-styled interface with a collapsible sidebar of sliders and a 4-tab main area. Here is an accurate recreation of the live UI:</p>

  <div class="app-preview-container">
    <div class="browser-chrome">
      <div class="browser-dots"><span></span><span></span><span></span></div>
      <div class="browser-url">localhost:5173 — Discrete Calabi–Yau Gauge Functor Dashboard</div>
    </div>

    <div class="app-inner">
      <!-- sidebar -->
      <div class="fake-sidebar">
        <div class="fake-label">MESH (4-TORUS)</div>
        <div class="fake-slider-group">
          <div class="fake-slider-row"><span>Grid nx</span><span style="color:var(--teal)">3</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill" style="width:40%"></div></div>
          <div class="fake-slider-row"><span>Grid ny</span><span style="color:var(--teal)">3</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill" style="width:40%"></div></div>
          <div class="fake-slider-row"><span>Grid nz</span><span style="color:var(--teal)">2</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill" style="width:20%"></div></div>
          <div class="fake-slider-row"><span>Grid nw</span><span style="color:var(--teal)">2</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill" style="width:20%"></div></div>
        </div>
        <div class="fake-label" style="color:var(--orange)">GAUGE FIELD</div>
        <div class="fake-slider-group">
          <div class="fake-slider-row"><span>Link scale ε</span><span style="color:var(--orange)">0.050</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill orange" style="width:15%"></div></div>
          <div class="fake-slider-row"><span>Lattice h²</span><span style="color:var(--orange)">0.010</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill orange" style="width:9%"></div></div>
          <div class="fake-slider-row"><span>Eigenvalues k</span><span style="color:var(--orange)">10</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill orange" style="width:42%"></div></div>
        </div>
        <div class="fake-label" style="color:var(--purple)">WALL-CROSSING</div>
        <div class="fake-slider-group">
          <div class="fake-slider-row"><span>μ₁ (split)</span><span style="color:var(--purple)">0.50</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill purple" style="width:60%"></div></div>
          <div class="fake-slider-row"><span>μ₂ (split)</span><span style="color:var(--purple)">-0.30</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill purple" style="width:35%"></div></div>
          <div class="fake-slider-row"><span>Sweep steps</span><span style="color:var(--purple)">12</span></div>
          <div class="fake-slider-track"><div class="fake-slider-fill purple" style="width:55%"></div></div>
        </div>
        <div style="margin-top:auto">
          <div class="fake-run-btn">▶ RUN SIMULATION</div>
          <div style="height:8px"></div>
          <div class="fake-run-btn" style="color:var(--orange);border-color:rgba(249,115,22,0.3);background:rgba(249,115,22,0.1)">⟳ WALL CROSSING</div>
        </div>
      </div>

      <!-- main -->
      <div class="fake-main">
        <div class="fake-stat-row">
          <div class="fake-stat">
            <div class="fake-stat-label">MESH nV/nE/nF</div>
            <div class="fake-stat-val">36·144·216</div>
          </div>
          <div class="fake-stat">
            <div class="fake-stat-label">SLOPE λ₁</div>
            <div class="fake-stat-val">0.00312</div>
          </div>
          <div class="fake-stat">
            <div class="fake-stat-label">SLOPE λ₂</div>
            <div class="fake-stat-val orange">-0.00312</div>
          </div>
          <div class="fake-stat">
            <div class="fake-stat-label">GAUGE DIM</div>
            <div class="fake-stat-val purple">4</div>
          </div>
          <div class="fake-stat">
            <div class="fake-stat-label">ZERO MODES</div>
            <div class="fake-stat-val" style="color:var(--yellow)">1</div>
          </div>
        </div>
        <div class="fake-tabs">
          <div class="fake-tab active">CURVATURE</div>
          <div class="fake-tab">WALL-CROSSING</div>
          <div class="fake-tab">SPECTRUM</div>
          <div class="fake-tab">DATA</div>
        </div>
        <div class="fake-canvas-area">
          <canvas id="ui-canvas"></canvas>
        </div>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ MATH ═══ -->
<section id="math">
  <div class="section-label">03 · Mathematics</div>
  <h2>The Numerical Pipeline</h2>
  <p>Every calculation is performed server-side in real numpy/scipy. The diagram below shows the exact computation graph.</p>

  <div class="diagram-card" style="margin-top:20px">
    <div class="diagram-card-header">PIPELINE — T⁴ MESH → GAUGE FIELD → CURVATURE → SPECTRUM</div>
    <canvas id="pipeline-canvas" height="300"></canvas>
  </div>

  <div class="math-diagram-wrapper" style="margin-top:20px">
    <div class="diagram-card">
      <div class="diagram-card-header">WALL-CROSSING — SLOPE FILTRATION λ(t)</div>
      <canvas id="wall-canvas" height="200"></canvas>
    </div>
    <div class="diagram-card">
      <div class="diagram-card-header">DOLBEAULT SPECTRUM — LAPLACIAN EIGENVALUES</div>
      <canvas id="spec-canvas" height="200"></canvas>
    </div>
  </div>

  <div class="math-diagram-wrapper" style="margin-top:20px">
    <div class="diagram-card" style="grid-column: 1 / -1;">
      <div class="diagram-card-header">FACE CURVATURE HEATMAP — ‖F_f‖ PER FACE</div>
      <canvas id="heat-canvas" height="160"></canvas>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ ARCHITECTURE ═══ -->
<section id="architecture">
  <div class="section-label">04 · Architecture</div>
  <h2>System Design</h2>

  <div class="arch-grid">
    <div class="arch-card">
      <h3>Repository Structure</h3>
      <div class="file-tree">
        <div class="root">cy-gauge-app/</div>
        <div>├── <span class="py">main.py</span>            <span class="comment">← FastAPI backend</span></div>
        <div>├── <span class="cfg">requirements.txt</span>   <span class="comment">← Python deps</span></div>
        <div>├── <span class="cfg">Dockerfile</span>         <span class="comment">← Backend image</span></div>
        <div>│</div>
        <div>├── <span class="jsx">App.jsx</span>            <span class="comment">← React root (4 tabs)</span></div>
        <div>├── <span class="jsx">main.jsx</span>           <span class="comment">← Vite entry point</span></div>
        <div>├── <span class="cfg">index.html</span>         <span class="comment">← HTML shell</span></div>
        <div>├── <span class="cfg">package.json</span>       <span class="comment">← Node deps</span></div>
        <div>├── <span class="cfg">vite.config.js</span>     <span class="comment">← Proxy → :8000</span></div>
        <div>│</div>
        <div>└── <span class="cfg">docker-compose.yml</span> <span class="comment">← Orchestration</span></div>
      </div>
    </div>

    <div class="arch-card">
      <h3>Technology Stack</h3>
      <table>
        <thead><tr><th>Layer</th><th>Technology</th></tr></thead>
        <tbody>
          <tr><td>Frontend</td><td>React 18 + Vite 5</td></tr>
          <tr><td>Visualisation</td><td>Raw HTML5 &lt;canvas&gt;</td></tr>
          <tr><td>Backend</td><td>FastAPI 0.115</td></tr>
          <tr><td>Linear algebra</td><td>NumPy, SciPy</td></tr>
          <tr><td>Sparse solvers</td><td>eigsh + splu (shift-invert)</td></tr>
          <tr><td>Matrix exp</td><td>scipy.linalg.expm</td></tr>
          <tr><td>Containers</td><td>Docker + docker-compose</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="diagram-card" style="margin-top:20px">
    <div class="diagram-card-header">REQUEST / RESPONSE FLOW</div>
    <canvas id="flow-canvas" height="200"></canvas>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ TABS ═══ -->
<section id="tabs">
  <div class="section-label">05 · Dashboard Tabs</div>
  <h2>Four Interactive Views</h2>

  <div class="arch-grid" style="grid-template-columns: repeat(auto-fit, minmax(220px,1fr));">
    <div class="arch-card">
      <h3 style="color:var(--teal)">① Curvature</h3>
      <p>Heatmap of per-face curvature norms <strong style="color:var(--text)">‖F_f‖</strong> from real <code style="color:var(--teal)">face_holonomies()</code>. Colour encodes magnitude: cold (low) → warm (high). Cell labels appear when the mesh is small enough to read.</p>
    </div>
    <div class="arch-card">
      <h3 style="color:var(--orange)">② Wall-Crossing</h3>
      <p>Line chart of slope eigenvalues <strong style="color:var(--text)">λ₁(t)</strong> <span style="color:var(--teal)">(teal)</span> and <strong style="color:var(--text)">λ₂(t)</strong> <span style="color:var(--orange)">(orange)</span> across the bundle-mixing sweep t ∈ [0,1]. A sign change marks a Harder–Narasimhan wall.</p>
    </div>
    <div class="arch-card">
      <h3 style="color:var(--purple)">③ Spectrum</h3>
      <p>Bar chart of the first <em>k</em> eigenvalues of the FEEC Dolbeault Laplacian <strong style="color:var(--text)">Δ = ∂̄†∂̄</strong> via sparse <code style="color:var(--teal)">eigsh</code> shift-invert. Eigenvalues below 1e-7 are counted as <strong style="color:var(--yellow)">zero modes</strong>.</p>
    </div>
    <div class="arch-card">
      <h3 style="color:var(--yellow)">④ Data</h3>
      <p>Raw numerical output table: mesh topology (nV/nE/nF), slope values and Δλ, Φ trace and norm, gauge algebra dimension vs u(N), curvature statistics, and the full eigenvalue array.</p>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ API ═══ -->
<section id="api">
  <div class="section-label">06 · API Reference</div>
  <h2>REST Endpoints</h2>
  <p>Base URL (local): <code style="color:var(--teal)">http://localhost:8000</code> &nbsp;·&nbsp; Swagger UI: <code style="color:var(--teal)">http://localhost:8000/docs</code></p>

  <div class="api-section">
    <div class="api-endpoint">
      <div class="api-header">
        <div class="api-method get">GET</div>
        <div class="api-path">/api/health</div>
        <div class="api-desc">Liveness check</div>
      </div>
      <div class="api-body">
        <p style="margin:0;font-size:12px">Returns <code style="color:var(--teal)">{"status":"ok"}</code></p>
      </div>
    </div>

    <div class="api-endpoint">
      <div class="api-header">
        <div class="api-method post">POST</div>
        <div class="api-path">/api/run</div>
        <div class="api-desc">Full simulation — mesh + gauge + Laplacian</div>
      </div>
      <div class="api-body">
        <table>
          <thead><tr><th>Field</th><th>Type</th><th>Default</th><th>Range</th><th>Description</th></tr></thead>
          <tbody>
            <tr><td>nx, ny</td><td>int</td><td>3</td><td>2–5</td><td>Grid points along x / y</td></tr>
            <tr><td>nz, nw</td><td>int</td><td>2</td><td>2–4</td><td>Grid points along z / w</td></tr>
            <tr><td>N</td><td>int</td><td>2</td><td>2–3</td><td>U(N) gauge group rank</td></tr>
            <tr><td>scale</td><td>float</td><td>0.05</td><td>0.001–0.5</td><td>Link scale ε</td></tr>
            <tr><td>h2</td><td>float</td><td>0.01</td><td>0.001–0.2</td><td>Lattice spacing h²</td></tr>
            <tr><td>seed</td><td>int</td><td>42</td><td>0–9999</td><td>RNG seed</td></tr>
            <tr><td>n_eigs</td><td>int</td><td>10</td><td>2–30</td><td>Dolbeault eigenvalues</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="api-endpoint">
      <div class="api-header">
        <div class="api-method post">POST</div>
        <div class="api-path">/api/sweep</div>
        <div class="api-desc">Wall-crossing sweep over mixing t</div>
      </div>
      <div class="api-body">
        <table>
          <thead><tr><th>Extra Field</th><th>Type</th><th>Default</th><th>Description</th></tr></thead>
          <tbody>
            <tr><td>mu1</td><td>float</td><td>0.5</td><td>Split-bundle phase μ₁ ∈ [−2, 2]</td></tr>
            <tr><td>mu2</td><td>float</td><td>−0.3</td><td>Split-bundle phase μ₂ ∈ [−2, 2]</td></tr>
            <tr><td>steps</td><td>int</td><td>12</td><td>Number of t ∈ [0,1] sweep points</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ QUICK START ═══ -->
<section id="quick-start">
  <div class="section-label">07 · Quick Start</div>
  <h2>Get Running in 60 Seconds</h2>

  <div class="quick-start-grid">
    <div class="qs-card">
      <h3>🐳 Docker (Recommended)</h3>
      <div class="code-label">SHELL</div>
      <div class="code-block">
        <span class="comment"># Clone & launch everything</span><br/>
        <span class="cmd">git clone</span> https://github.com/<br/>
        &nbsp;&nbsp;ashpeterpark-beep/cy-gauge-app<br/>
        <span class="cmd">cd</span> cy-gauge-app<br/>
        <span class="cmd">docker-compose up --build</span>
      </div>
      <div style="margin-top:12px">
        <table>
          <thead><tr><th>Service</th><th>URL</th></tr></thead>
          <tbody>
            <tr><td>Frontend</td><td><span style="color:var(--teal)">localhost:5173</span></td></tr>
            <tr><td>Backend API</td><td><span style="color:var(--teal)">localhost:8000</span></td></tr>
            <tr><td>Swagger docs</td><td><span style="color:var(--teal)">localhost:8000/docs</span></td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="qs-card">
      <h3>⚙️ Manual Setup</h3>
      <div class="code-label">BACKEND</div>
      <div class="code-block">
        <span class="cmd">python -m venv</span> venv<br/>
        <span class="cmd">source</span> venv/bin/activate<br/>
        <span class="cmd">pip install</span> -r requirements.txt<br/>
        <span class="cmd">uvicorn</span> main:app --reload --port 8000
      </div>
      <div class="code-label" style="margin-top:10px">FRONTEND</div>
      <div class="code-block">
        <span class="cmd">npm install</span><br/>
        <span class="cmd">npm run dev</span>
      </div>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ DEPLOY ═══ -->
<section id="deploy">
  <div class="section-label">08 · Deployment</div>
  <h2>Cloud Deployment Options</h2>

  <div class="arch-grid">
    <div class="arch-card">
      <h3>Backend → Railway / Render</h3>
      <p>Push the repo to GitHub, connect to Railway or Render, and set the start command:</p>
      <div class="code-block" style="font-size:11px">uvicorn main:app --host 0.0.0.0 --port <span class="url">$PORT</span></div>
    </div>
    <div class="arch-card">
      <h3>Frontend → Vercel / Netlify</h3>
      <div class="code-block" style="font-size:11px">
        <span class="cmd">npm run build</span> <span class="comment"># outputs dist/</span>
      </div>
      <p>Upload <code style="color:var(--teal)">dist/</code> to Vercel. Add environment variable:</p>
      <div class="code-block" style="font-size:11px">VITE_API_URL=https://<span class="url">your-backend.railway.app</span></div>
    </div>
    <div class="arch-card">
      <h3>Free Tier: Hugging Face Spaces</h3>
      <p>Use a Docker Space and copy <code style="color:var(--teal)">docker-compose.yml</code> into the Space configuration. Deploy the FastAPI backend as a standalone Space and host the frontend on Vercel for full free-tier hosting.</p>
    </div>
    <div class="arch-card">
      <h3>Performance Notes</h3>
      <p>Large meshes (nx=ny=5, nz=nw=4) with k=30 eigenvalues can take several seconds on a single CPU core. The FEEC Laplacian matrix grows as O(nE · N). Recommended defaults: nx=ny=3, nz=nw=2, k=10.</p>
    </div>
  </div>
</section>

<div class="divider"></div>

<!-- ═══════════════════════════════════════════ FOOTER ═══ -->
<footer>
  <div class="footer-title">cy-gauge-app</div>
  <div class="footer-sub">DISCRETE CALABI–YAU GAUGE FUNCTOR DASHBOARD</div>
  <div class="footer-links">
    <a href="https://github.com/ashpeterpark-beep/cy-gauge-app">GitHub</a>
    <a href="https://github.com/ashpeterpark-beep/cy-gauge-app/blob/main/LICENSE..%20md">MIT License</a>
    <a href="https://twitter.com/GaiusLumen">@GaiusLumen</a>
    <a href="mailto:gaiuslumen@gmail.com">Contact</a>
  </div>
  <div style="margin-top:24px;font-family:'Space Mono',monospace;font-size:8px;color:var(--dim);letter-spacing:2px">
    Built with FastAPI · NumPy · SciPy · React · Vite · Docker · MIT © Gaius Lumen
  </div>
</footer>

<script>
// ══════════════════════════════════════════════
//  HERO — 3D rotating 4-torus point cloud (WebGL-style via 2D canvas)
// ══════════════════════════════════════════════
(function() {
  const canvas = document.getElementById('hero-canvas');
  const ctx = canvas.getContext('2d');
  let W, H, pts;
  let t = 0;

  function resize() {
    W = canvas.width  = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
    buildPoints();
  }

  function buildPoints() {
    pts = [];
    const NX=6,NY=6,NZ=5,NW=4;
    for (let i=0;i<NX;i++) for (let j=0;j<NY;j++) for (let k=0;k<NZ;k++) for (let l=0;l<NW;l++) {
      pts.push({
        x: (i/NX)*2*Math.PI,
        y: (j/NY)*2*Math.PI,
        z: (k/NZ)*2*Math.PI,
        w: (l/NW)*2*Math.PI,
      });
    }
  }

  function project(p, angle1, angle2, angle3) {
    // 4D → 3D → 2D
    const ca1=Math.cos(angle1), sa1=Math.sin(angle1);
    const ca2=Math.cos(angle2), sa2=Math.sin(angle2);
    const ca3=Math.cos(angle3), sa3=Math.sin(angle3);

    // embed each torus coordinate as 4D point on product of circles
    const R1=1.2, r1=0.5, R2=0.9, r2=0.3;
    const sx = (R1 + r1*Math.cos(p.z)) * Math.cos(p.x);
    const sy = (R1 + r1*Math.cos(p.z)) * Math.sin(p.x);
    const sz = r1 * Math.sin(p.z);
    const sw = (R2 + r2*Math.cos(p.w)) * Math.sin(p.y) * 0.6;

    // rotate xz
    const rx1 = sx*ca1 - sz*sa1;
    const ry1 = sy;
    const rz1 = sx*sa1 + sz*ca1;

    // rotate yw
    const rx2 = rx1;
    const ry2 = ry1*ca2 - sw*sa2;
    const rz2 = rz1;
    const rw2 = ry1*sa2 + sw*ca2;

    // project 4D to 3D
    const dist4 = 4.5;
    const w3 = 1/(dist4 - rw2);
    const px3 = rx2*w3, py3 = ry2*w3, pz3 = rz2*w3;

    // rotate in 3D
    const rpx = px3*ca3 - pz3*sa3;
    const rpy = py3;
    const rpz = px3*sa3 + pz3*ca3;

    // perspective project to 2D
    const dist3 = 3.5;
    const scale = dist3/(dist3+rpz);
    return {
      px: W/2 + rpx * scale * Math.min(W,H)*0.28,
      py: H/2 + rpy * scale * Math.min(W,H)*0.28,
      z: rpz,
      depth: scale
    };
  }

  function draw() {
    ctx.clearRect(0,0,W,H);

    // background gradient
    const g = ctx.createRadialGradient(W/2,H/2,0,W/2,H/2,Math.max(W,H)*0.7);
    g.addColorStop(0,'rgba(10,20,40,0.95)');
    g.addColorStop(1,'rgba(6,8,16,1)');
    ctx.fillStyle = g;
    ctx.fillRect(0,0,W,H);

    const a1 = t*0.3, a2 = t*0.2, a3 = t*0.15;
    const projected = pts.map(p => project(p, a1, a2, a3));

    // Draw edges (nearest neighbours)
    const NX=6,NY=6,NZ=5,NW=4;
    const total = NX*NY*NZ*NW;
    ctx.lineWidth = 0.5;
    for (let i=0;i<projected.length;i++) {
      for (let j=i+1;j<projected.length;j++) {
        const dx=projected[i].px-projected[j].px, dy=projected[i].py-projected[j].py;
        const d2 = dx*dx+dy*dy;
        if (d2 < (Math.min(W,H)*0.06)**2) {
          const alpha = 0.08 * projected[i].depth * projected[j].depth * 3;
          ctx.strokeStyle = `rgba(78,232,208,${Math.min(alpha,0.18)})`;
          ctx.beginPath();
          ctx.moveTo(projected[i].px, projected[i].py);
          ctx.lineTo(projected[j].px, projected[j].py);
          ctx.stroke();
        }
      }
    }

    // Draw points
    projected.forEach((p,i) => {
      const s = Math.max(1.5, 4 * p.depth);
      const alpha = 0.4 + p.depth*0.4;
      // colour by torus coordinate
      const hue = (i/projected.length)*200 + 160;
      ctx.beginPath();
      ctx.arc(p.px, p.py, s, 0, Math.PI*2);
      ctx.fillStyle = `hsla(${hue}, 80%, 70%, ${alpha})`;
      ctx.fill();
    });

    // Glow overlay
    const g2 = ctx.createRadialGradient(W/2,H*0.45,0,W/2,H*0.45,Math.min(W,H)*0.35);
    g2.addColorStop(0,'rgba(78,232,208,0.04)');
    g2.addColorStop(1,'transparent');
    ctx.fillStyle = g2;
    ctx.fillRect(0,0,W,H);

    t += 0.004;
    requestAnimationFrame(draw);
  }

  window.addEventListener('resize', resize);
  resize();
  draw();
})();


// ══════════════════════════════════════════════
//  UI CANVAS — live curvature heatmap animation
// ══════════════════════════════════════════════
(function() {
  const canvas = document.getElementById('ui-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let phase = 0;

  function resize() {
    canvas.width  = canvas.offsetWidth  || 600;
    canvas.height = canvas.offsetHeight || 250;
  }
  resize();
  new ResizeObserver(resize).observe(canvas);

  function drawHeat() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0,0,W,H);
    const N = 15;
    const cw = W/N, ch = H/N;
    for (let row=0;row<N;row++) for (let col=0;col<N;col++) {
      const base = Math.sin(row*0.8 + phase)*0.5 + Math.cos(col*0.7 - phase*0.7)*0.5;
      const t = (base+1)/2;
      const r = Math.round(20  + t*220);
      const g = Math.round(180 - t*150);
      const b = Math.round(240 - t*200);
      ctx.fillStyle = `rgb(${r},${g},${b})`;
      ctx.fillRect(col*cw+1, row*ch+1, cw-2, ch-2);
      if (cw > 22) {
        ctx.fillStyle = 'rgba(0,0,0,0.5)';
        ctx.font = `${Math.max(7,cw*0.22)}px monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(t.toFixed(2), col*cw+cw/2, row*ch+ch/2);
      }
    }
    phase += 0.012;
    requestAnimationFrame(drawHeat);
  }
  drawHeat();
})();


// ══════════════════════════════════════════════
//  PIPELINE DIAGRAM CANVAS
// ══════════════════════════════════════════════
(function() {
  const canvas = document.getElementById('pipeline-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() { canvas.width = canvas.offsetWidth || 900; draw(); }
  window.addEventListener('resize', resize);
  resize();

  function draw() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0,0,W,H);

    const steps = [
      { label: 'T⁴ LATTICE\nMESH',    color: '#4ee8d0', sub: 'build_torus4d()' },
      { label: 'SU(N) LINK\nVARIABLES', color: '#4ee8d0', sub: 'random_suN_links()' },
      { label: 'FACE\nHOLONOMIES',    color: '#f97316', sub: 'face_holonomies()' },
      { label: 'HERMITIAN\nENDOMORPH', color: '#f97316', sub: 'herm_endomorphism()' },
      { label: 'SLOPE\nFILTRATION',   color: '#c084fc', sub: 'slope_filtration()' },
      { label: 'DOLBEAULT\nSPECTRUM', color: '#c084fc', sub: 'dolbeault_spectrum()' },
    ];

    const n = steps.length;
    const pad = 30;
    const totalW = W - pad*2;
    const boxW = Math.min(110, (totalW - (n-1)*20) / n);
    const boxH = 72;
    const startX = (W - (n*boxW + (n-1)*24)) / 2;
    const cy = H / 2;

    steps.forEach((s, i) => {
      const x = startX + i*(boxW+24);
      const y = cy - boxH/2;

      // arrow
      if (i > 0) {
        const ax = x - 24, ay = cy;
        ctx.strokeStyle = 'rgba(255,255,255,0.12)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([4,3]);
        ctx.beginPath(); ctx.moveTo(ax-boxW*0.0, ay); ctx.lineTo(ax+22, ay); ctx.stroke();
        ctx.setLineDash([]);
        // arrowhead
        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        ctx.beginPath();
        ctx.moveTo(ax+22, ay-4);
        ctx.lineTo(ax+28, ay);
        ctx.lineTo(ax+22, ay+4);
        ctx.fill();
      }

      // box
      ctx.fillStyle = 'rgba(255,255,255,0.03)';
      ctx.strokeStyle = s.color + '44';
      ctx.lineWidth = 1;
      ctx.fillRect(x, y, boxW, boxH);
      ctx.strokeRect(x, y, boxW, boxH);

      // top colour bar
      ctx.fillStyle = s.color + '22';
      ctx.fillRect(x, y, boxW, 4);
      ctx.fillStyle = s.color;
      ctx.fillRect(x, y, boxW*0.35, 3);

      // label
      ctx.font = `bold ${Math.min(9, boxW*0.085)}px 'Space Mono', monospace`;
      ctx.fillStyle = '#e2e8f0';
      ctx.textAlign = 'center';
      const lines = s.label.split('\n');
      lines.forEach((l, li) => {
        ctx.fillText(l, x + boxW/2, y + 22 + li*14);
      });

      // sub
      ctx.font = `${Math.min(7, boxW*0.065)}px 'Space Mono', monospace`;
      ctx.fillStyle = s.color;
      ctx.fillText(s.sub, x + boxW/2, y + boxH - 10);
    });
  }
})();


// ══════════════════════════════════════════════
//  WALL-CROSSING CANVAS
// ══════════════════════════════════════════════
(function() {
  const canvas = document.getElementById('wall-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let ph = 0;

  function resize() { canvas.width = canvas.offsetWidth || 500; }
  resize();
  new ResizeObserver(() => { resize(); }).observe(canvas);

  function draw() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0,0,W,H);

    const pad = {l:40, r:16, t:16, b:32};
    const pw = W-pad.l-pad.r, pheight = H-pad.t-pad.b;

    // grid
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth = 1;
    for (let i=0;i<=4;i++) {
      const y = pad.t + i*pheight/4;
      ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(pad.l+pw, y); ctx.stroke();
    }

    // zero line
    ctx.strokeStyle = 'rgba(250,204,21,0.25)';
    ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(pad.l, pad.t+pheight/2); ctx.lineTo(pad.l+pw, pad.t+pheight/2); ctx.stroke();
    ctx.setLineDash([]);

    // axes
    ctx.strokeStyle = 'rgba(255,255,255,0.15)';
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, pad.t+pheight); ctx.lineTo(pad.l+pw, pad.t+pheight); ctx.stroke();

    const N = 30;
    // λ₁ — starts positive, crosses zero
    const series1 = Array.from({length:N}, (_,i) => {
      const t = i/(N-1);
      return 0.35 - 0.72*t + 0.08*Math.sin(t*8+ph)*Math.exp(-t*2);
    });
    // λ₂ — mirror
    const series2 = series1.map(v => -v + 0.015*Math.sin(ph*1.3));

    function plotLine(data, color) {
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.shadowColor = color; ctx.shadowBlur = 5;
      ctx.beginPath();
      data.forEach((v, i) => {
        const x = pad.l + (i/(N-1))*pw;
        const y = pad.t + pheight/2 - v*pheight*0.95;
        i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
      });
      ctx.stroke();
      ctx.shadowBlur = 0;
      // dots
      ctx.fillStyle = color;
      data.forEach((v,i) => {
        const x = pad.l + (i/(N-1))*pw;
        const y = pad.t + pheight/2 - v*pheight*0.95;
        ctx.beginPath(); ctx.arc(x,y,2.5,0,Math.PI*2); ctx.fill();
      });
    }

    plotLine(series1, '#4ee8d0');
    plotLine(series2, '#f97316');

    // labels
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.font = '8px Space Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('0', pad.l+pw/2, pad.t+pheight+16);
    ctx.fillText('0.5', pad.l, pad.t+pheight+16);
    ctx.fillText('1', pad.l+pw, pad.t+pheight+16);

    ph += 0.01;
    requestAnimationFrame(draw);
  }
  draw();
})();


// ══════════════════════════════════════════════
//  SPECTRUM CANVAS
// ══════════════════════════════════════════════
(function() {
  const canvas = document.getElementById('spec-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let ph = 0;

  function resize() { canvas.width = canvas.offsetWidth || 500; }
  resize();
  new ResizeObserver(resize).observe(canvas);

  function draw() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0,0,W,H);

    const pad = {l:38, r:14, t:14, b:30};
    const pw = W-pad.l-pad.r, ph2 = H-pad.t-pad.b;

    // Simulated eigenvalues: 1 zero mode then growing
    const eigs = [1e-9, 0.002+0.0005*Math.sin(ph*0.7), 0.008, 0.015, 0.026, 0.041, 0.059, 0.08, 0.104, 0.132];
    const maxV = eigs[eigs.length-1];
    const barW = pw / eigs.length;

    eigs.forEach((v, i) => {
      const h = (v/maxV)*ph2;
      const x = pad.l + i*barW;
      const t2 = i/eigs.length;
      const isZero = v < 1e-6;
      if (isZero) {
        ctx.fillStyle = '#facc15';
      } else {
        ctx.fillStyle = `hsl(${160+t2*80}, 65%, ${35+t2*22}%)`;
      }
      ctx.fillRect(x+1, pad.t+ph2-h, barW-2, h);
    });

    ctx.strokeStyle = 'rgba(255,255,255,0.15)';
    ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, pad.t+ph2); ctx.lineTo(pad.l+pw, pad.t+ph2); ctx.stroke();

    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    ctx.font = '8px Space Mono, monospace';
    ctx.textAlign = 'center';
    ctx.fillText('Eigenvalue index →', pad.l+pw/2, H-4);

    // zero mode label
    ctx.fillStyle = '#facc15';
    ctx.fillText('zero', pad.l+barW/2, pad.t+ph2-6);

    ph += 0.015;
    requestAnimationFrame(draw);
  }
  draw();
})();


// ══════════════════════════════════════════════
//  HEAT CANVAS (full-width)
// ══════════════════════════════════════════════
(function() {
  const canvas = document.getElementById('heat-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let phase = 0;

  function resize() { canvas.width = canvas.offsetWidth || 900; }
  resize();
  new ResizeObserver(resize).observe(canvas);

  function draw() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0,0,W,H);
    const COLS = 36, ROWS = 8;
    const cw = W/COLS, ch = H/ROWS;
    for (let r=0;r<ROWS;r++) for (let c=0;c<COLS;c++) {
      const v = (Math.sin(c*0.4+phase)*0.5 + Math.cos(r*0.8-phase*0.6)*0.5 + 1)/2;
      ctx.fillStyle = `rgb(${Math.round(20+v*220)},${Math.round(180-v*150)},${Math.round(240-v*200)})`;
      ctx.fillRect(c*cw+0.5, r*ch+0.5, cw-1, ch-1);
    }
    phase += 0.008;
    requestAnimationFrame(draw);
  }
  draw();
})();


// ══════════════════════════════════════════════
//  FLOW DIAGRAM CANVAS
// ══════════════════════════════════════════════
(function() {
  const canvas = document.getElementById('flow-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  function resize() { canvas.width = canvas.offsetWidth || 900; draw(); }
  window.addEventListener('resize', resize);
  resize();

  function draw() {
    const W = canvas.width, H = canvas.height;
    ctx.clearRect(0,0,W,H);

    const nodes = [
      { label: 'BROWSER\nREACT UI',    x: 0.08, y: 0.5,  color: '#4ee8d0', w: 110, h: 55 },
      { label: 'POST /api/run\nor /api/sweep', x: 0.33, y: 0.5,  color: '#f97316', w: 120, h: 50, small:true },
      { label: 'FASTAPI\nBACKEND',     x: 0.59, y: 0.5,  color: '#f97316', w: 110, h: 55 },
      { label: 'NumPy / SciPy\nPIPELINE', x: 0.84, y: 0.5,  color: '#c084fc', w: 120, h: 55 },
    ];

    nodes.forEach((n, i) => {
      const cx = n.x * W, cy = n.y * H;
      const x = cx - n.w/2, y = cy - n.h/2;

      // connector
      if (i < nodes.length-1) {
        const nx = nodes[i+1];
        const ex = nx.x * W - nx.w/2;
        ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        ctx.lineWidth = 1.5;
        ctx.setLineDash([5,4]);
        ctx.beginPath();
        ctx.moveTo(cx + n.w/2, cy);
        ctx.lineTo(ex, cy);
        ctx.stroke();
        ctx.setLineDash([]);

        // arrow
        ctx.fillStyle = 'rgba(255,255,255,0.2)';
        ctx.beginPath();
        ctx.moveTo(ex-1, cy-5); ctx.lineTo(ex+6, cy); ctx.lineTo(ex-1, cy+5); ctx.fill();

        // JSON label on 2nd connector (response)
        if (i===1) {
          ctx.font = '7px Space Mono, monospace';
          ctx.fillStyle = 'rgba(249,115,22,0.7)';
          ctx.textAlign = 'center';
          ctx.fillText('JSON response', (cx+n.w/2+ex)/2, cy - 8);
        }
      }

      // box
      ctx.fillStyle = 'rgba(255,255,255,0.03)';
      ctx.strokeStyle = n.color + '55';
      ctx.lineWidth = 1;
      ctx.fillRect(x, y, n.w, n.h);
      ctx.strokeRect(x, y, n.w, n.h);

      // top bar
      ctx.fillStyle = n.color + '30';
      ctx.fillRect(x, y, n.w, 3);

      ctx.font = `bold ${n.small ? 7.5 : 9}px 'Space Mono', monospace`;
      ctx.fillStyle = '#e2e8f0';
      ctx.textAlign = 'center';
      const ls = n.label.split('\n');
      ls.forEach((l,li) => ctx.fillText(l, cx, cy - (ls.length-1)*7 + li*14));
    });
  }
})();
</script>
</body>
</html>
