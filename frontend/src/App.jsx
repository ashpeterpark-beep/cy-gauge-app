 import { useState, useEffect, useRef, useCallback } from "react";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ─── Canvas helpers ────────────────────────────────────────────────────────────

function drawHeatmap(canvas, values, label) {
  if (!canvas || !values?.length) return;
  const ctx = canvas.getContext("2d");
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  const N = Math.ceil(Math.sqrt(values.length));
  const cw = W / N, ch = H / N;
  const max = Math.max(...values, 1e-10);
  values.forEach((v, i) => {
    const row = Math.floor(i / N), col = i % N;
    const t = v / max;
    ctx.fillStyle = `rgb(${Math.round(20 + t * 220)},${Math.round(180 - t * 150)},${Math.round(240 - t * 200)})`;
    ctx.fillRect(col * cw + 1, row * ch + 1, cw - 2, ch - 2);
    if (cw > 28) {
      ctx.fillStyle = "rgba(0,0,0,0.6)";
      ctx.font = `${Math.max(8, cw * 0.25)}px monospace`;
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(v.toFixed(2), col * cw + cw / 2, row * ch + ch / 2);
    }
  });
}

function drawLineChart(canvas, sweep, keys, colors, xKey = "t", xLabel = "mixing t", yLabel = "") {
  if (!canvas || !sweep?.length) return;
  const ctx = canvas.getContext("2d");
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  const pad = { l: 46, r: 16, t: 16, b: 38 };
  const pw = W - pad.l - pad.r, ph = H - pad.t - pad.b;

  const allY = sweep.flatMap(d => keys.flatMap(k => Array.isArray(d[k]) ? d[k] : [d[k]]));
  const yMin = Math.min(...allY), yMax = Math.max(...allY);
  const yRange = yMax - yMin || 1;
  const xMin = sweep[0][xKey], xMax = sweep[sweep.length - 1][xKey];
  const xRange = xMax - xMin || 1;

  const mx = x => pad.l + ((x - xMin) / xRange) * pw;
  const my = y => pad.t + ph - ((y - yMin) / yRange) * ph;

  // grid
  ctx.strokeStyle = "rgba(255,255,255,0.07)";
  ctx.lineWidth = 1;
  [0, 0.25, 0.5, 0.75, 1].forEach(r => {
    const y = pad.t + r * ph;
    ctx.beginPath(); ctx.moveTo(pad.l, y); ctx.lineTo(pad.l + pw, y); ctx.stroke();
  });

  // zero line
  if (yMin < 0 && yMax > 0) {
    ctx.strokeStyle = "rgba(250,204,21,0.35)";
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(pad.l, my(0)); ctx.lineTo(pad.l + pw, my(0)); ctx.stroke();
    ctx.setLineDash([]);
  }

  // axes
  ctx.strokeStyle = "rgba(255,255,255,0.25)";
  ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, pad.t + ph); ctx.lineTo(pad.l + pw, pad.t + ph); ctx.stroke();

  // series
  keys.forEach((key, ki) => {
    const color = colors[ki];
    // each sweep point may have array (slopes) or scalar
    const pts = sweep.map(d => ({ x: d[xKey], y: Array.isArray(d[key]) ? d[key][ki] ?? d[key][0] : d[key] }));
    ctx.strokeStyle = color;
    ctx.lineWidth = 2.5;
    ctx.shadowColor = color; ctx.shadowBlur = 6;
    ctx.beginPath();
    pts.forEach((p, i) => i === 0 ? ctx.moveTo(mx(p.x), my(p.y)) : ctx.lineTo(mx(p.x), my(p.y)));
    ctx.stroke();
    ctx.shadowBlur = 0;
    ctx.fillStyle = color;
    pts.forEach(p => { ctx.beginPath(); ctx.arc(mx(p.x), my(p.y), 3.5, 0, Math.PI * 2); ctx.fill(); });
  });

  // labels
  ctx.fillStyle = "rgba(255,255,255,0.4)";
  ctx.font = "9px monospace";
  ctx.textAlign = "right";
  ctx.fillText(yMax.toFixed(3), pad.l - 4, pad.t + 6);
  ctx.fillText(yMin.toFixed(3), pad.l - 4, pad.t + ph);
  ctx.textAlign = "center";
  [0, 0.5, 1].forEach(r => ctx.fillText((xMin + r * xRange).toFixed(1), pad.l + r * pw, pad.t + ph + 16));
  ctx.fillText(xLabel, pad.l + pw / 2, H - 4);
  ctx.save(); ctx.translate(12, pad.t + ph / 2); ctx.rotate(-Math.PI / 2);
  ctx.fillText(yLabel, 0, 0); ctx.restore();
}

function drawSpectrum(canvas, eigvals) {
  if (!canvas || !eigvals?.length) return;
  const ctx = canvas.getContext("2d");
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);
  const pad = { l: 46, r: 16, t: 16, b: 38 };
  const pw = W - pad.l - pad.r, ph = H - pad.t - pad.b;
  const max = Math.max(...eigvals, 1e-10);
  const barW = pw / eigvals.length;

  eigvals.forEach((v, i) => {
    const h = (v / max) * ph;
    const x = pad.l + i * barW;
    const t = i / eigvals.length;
    ctx.fillStyle = `hsl(${160 + t * 100}, 70%, ${35 + t * 25}%)`;
    ctx.fillRect(x + 1, pad.t + ph - h, barW - 2, h);
    if (barW > 20) {
      ctx.fillStyle = "rgba(255,255,255,0.4)";
      ctx.font = "8px monospace";
      ctx.textAlign = "center";
      ctx.fillText(v.toExponential(1), x + barW / 2, pad.t + ph + 14);
    }
  });

  ctx.strokeStyle = "rgba(255,255,255,0.2)";
  ctx.lineWidth = 1.5;
  ctx.beginPath(); ctx.moveTo(pad.l, pad.t); ctx.lineTo(pad.l, pad.t + ph); ctx.lineTo(pad.l + pw, pad.t + ph); ctx.stroke();

  ctx.fillStyle = "rgba(255,255,255,0.35)";
  ctx.font = "9px monospace";
  ctx.textAlign = "center";
  ctx.fillText("Dolbeault Laplacian spectrum", pad.l + pw / 2, H - 2);
}

// ─── Slider ────────────────────────────────────────────────────────────────────

function Slider({ label, value, min, max, step, onChange, color = "#4ee8d0", fmt = v => v }) {
  return (
    <div style={{ marginBottom: "16px" }}>
      <div style={{ fontSize: "9px", color: "rgba(255,255,255,0.4)", letterSpacing: "1.5px", display: "flex", justifyContent: "space-between", marginBottom: "5px" }}>
        <span>{label}</span>
        <span style={{ color }}>{fmt(value)}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(Number(e.target.value))}
        style={{ width: "100%", accentColor: color, cursor: "pointer", height: "3px" }} />
    </div>
  );
}

// ─── StatPill ──────────────────────────────────────────────────────────────────

function StatPill({ label, value, color = "#e2e8f0", sub }) {
  return (
    <div style={{ padding: "8px 14px", background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.07)", minWidth: "100px" }}>
      <div style={{ fontSize: "8px", color: "rgba(255,255,255,0.28)", letterSpacing: "2px", marginBottom: "3px" }}>{label}</div>
      <div style={{ fontSize: "16px", color, fontWeight: 400 }}>{value ?? "—"}</div>
      {sub && <div style={{ fontSize: "8px", color: "rgba(255,255,255,0.2)", marginTop: "2px" }}>{sub}</div>}
    </div>
  );
}

// ─── Main App ──────────────────────────────────────────────────────────────────

const TABS = ["Curvature", "Wall-Crossing", "Spectrum", "Data"];

const DEFAULT_RUN = { nx: 3, ny: 3, nz: 2, nw: 2, N: 2, scale: 0.05, h2: 0.01, seed: 42, n_eigs: 10 };
const DEFAULT_SWEEP = { nx: 3, ny: 3, nz: 2, nw: 2, N: 2, scale: 0.05, h2: 0.01, mu1: 0.5, mu2: -0.3, seed: 42, steps: 12 };

export default function App() {
  const [runP, setRunP] = useState(DEFAULT_RUN);
  const [sweepP, setSweepP] = useState(DEFAULT_SWEEP);
  const [runData, setRunData] = useState(null);
  const [sweepData, setSweepData] = useState(null);
  const [tab, setTab] = useState("Curvature");
  const [loading, setLoading] = useState({ run: false, sweep: false });
  const [error, setError] = useState(null);
  const heatRef = useRef(null);
  const lineRef = useRef(null);
  const specRef = useRef(null);

  const setR = (k, v) => setRunP(p => ({ ...p, [k]: v }));
  const setS = (k, v) => setSweepP(p => ({ ...p, [k]: v }));

  const fetchRun = useCallback(async () => {
    setLoading(l => ({ ...l, run: true }));
    setError(null);
    try {
      const res = await fetch(`${API}/api/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(runP),
      });
      if (!res.ok) throw new Error(await res.text());
      setRunData(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(l => ({ ...l, run: false }));
    }
  }, [runP]);

  const fetchSweep = useCallback(async () => {
    setLoading(l => ({ ...l, sweep: true }));
    setError(null);
    try {
      const res = await fetch(`${API}/api/sweep`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(sweepP),
      });
      if (!res.ok) throw new Error(await res.text());
      setSweepData(await res.json());
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(l => ({ ...l, sweep: false }));
    }
  }, [sweepP]);

  // draw
  useEffect(() => { if (runData && heatRef.current) drawHeatmap(heatRef.current, runData.curv_norms, "‖F‖"); }, [runData, tab]);
  useEffect(() => {
    if (sweepData && lineRef.current)
      drawLineChart(lineRef.current, sweepData.sweep,
        ["slopes", "slopes"], ["#4ee8d0", "#f97316"], "t", "mixing t", "slope λ");
  }, [sweepData, tab]);
  useEffect(() => { if (runData && specRef.current) drawSpectrum(specRef.current, runData.dolbeault_eigenvalues); }, [runData, tab]);

  const isLoading = loading.run || loading.sweep;

  return (
    <div style={{
      minHeight: "100vh", background: "#080910", color: "#e2e8f0",
      fontFamily: "'Space Mono', 'Courier New', monospace", display: "flex", flexDirection: "column",
    }}>
      {/* Header */}
      <header style={{ borderBottom: "1px solid rgba(78,232,208,0.12)", padding: "16px 28px 12px", display: "flex", alignItems: "flex-end", gap: "20px", background: "linear-gradient(90deg,rgba(78,232,208,0.03) 0%,transparent 60%)" }}>
        <div>
          <div style={{ fontSize: "8px", letterSpacing: "4px", color: "#4ee8d0", marginBottom: "3px" }}>DISCRETE CALABI–YAU</div>
          <h1 style={{ margin: 0, fontSize: "20px", fontWeight: 400, color: "#fff", letterSpacing: "1px" }}>
            Gauge Functor <span style={{ color: "#4ee8d0" }}>⊗</span> Dashboard
          </h1>
        </div>
        <div style={{ flex: 1 }} />
        <div style={{ fontSize: "8px", color: "rgba(255,255,255,0.2)", letterSpacing: "2px", lineHeight: 2, textAlign: "right" }}>
          FASTAPI BACKEND<br />FULL SCIPY PIPELINE<br />SPARSE EIGSH
        </div>
      </header>

      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        {/* Sidebar */}
        <aside style={{ width: "230px", minWidth: "210px", background: "rgba(255,255,255,0.015)", borderRight: "1px solid rgba(255,255,255,0.05)", padding: "18px 14px", display: "flex", flexDirection: "column", overflowY: "auto" }}>

          <div style={{ fontSize: "8px", letterSpacing: "3px", color: "#4ee8d0", marginBottom: "14px" }}>MESH (4-TORUS)</div>
          {[["nx", "Grid nx", 2, 5, 1], ["ny", "Grid ny", 2, 5, 1], ["nz", "Grid nz", 2, 4, 1], ["nw", "Grid nw", 2, 4, 1]].map(([k, l, mn, mx, st]) => (
            <Slider key={k} label={l} value={runP[k]} min={mn} max={mx} step={st} onChange={v => { setR(k, v); setS(k, v); }} />
          ))}

          <div style={{ height: "1px", background: "rgba(255,255,255,0.05)", margin: "8px 0 14px" }} />
          <div style={{ fontSize: "8px", letterSpacing: "3px", color: "#f97316", marginBottom: "14px" }}>GAUGE FIELD</div>
          <Slider label="Link scale ε" value={runP.scale} min={0.01} max={0.3} step={0.01} color="#f97316" fmt={v => v.toFixed(3)} onChange={v => { setR("scale", v); setS("scale", v); }} />
          <Slider label="Lattice h²" value={runP.h2} min={0.001} max={0.1} step={0.001} color="#f97316" fmt={v => v.toFixed(3)} onChange={v => { setR("h2", v); setS("h2", v); }} />
          <Slider label="Eigenvalues k" value={runP.n_eigs} min={2} max={20} step={1} color="#f97316" onChange={v => setR("n_eigs", v)} />

          <div style={{ height: "1px", background: "rgba(255,255,255,0.05)", margin: "8px 0 14px" }} />
          <div style={{ fontSize: "8px", letterSpacing: "3px", color: "#c084fc", marginBottom: "14px" }}>WALL-CROSSING</div>
          <Slider label="μ₁ (split)" value={sweepP.mu1} min={-1} max={1} step={0.05} color="#c084fc" fmt={v => v.toFixed(2)} onChange={v => setS("mu1", v)} />
          <Slider label="μ₂ (split)" value={sweepP.mu2} min={-1} max={1} step={0.05} color="#c084fc" fmt={v => v.toFixed(2)} onChange={v => setS("mu2", v)} />
          <Slider label="Sweep steps" value={sweepP.steps} min={5} max={25} step={1} color="#c084fc" onChange={v => setS("steps", v)} />

          <div style={{ height: "1px", background: "rgba(255,255,255,0.05)", margin: "8px 0 14px" }} />
          <Slider label="RNG seed" value={runP.seed} min={0} max={200} step={1} color="rgba(255,255,255,0.35)" onChange={v => { setR("seed", v); setS("seed", v); }} />

          <div style={{ flex: 1 }} />
          <div style={{ display: "flex", flexDirection: "column", gap: "8px", marginTop: "12px" }}>
            <button onClick={fetchRun} disabled={loading.run} style={{ padding: "9px", background: loading.run ? "rgba(78,232,208,0.06)" : "rgba(78,232,208,0.12)", border: "1px solid rgba(78,232,208,0.3)", color: loading.run ? "rgba(78,232,208,0.3)" : "#4ee8d0", fontSize: "9px", letterSpacing: "3px", cursor: loading.run ? "not-allowed" : "pointer", textTransform: "uppercase" }}>
              {loading.run ? "RUNNING…" : "RUN SIMULATION"}
            </button>
            <button onClick={fetchSweep} disabled={loading.sweep} style={{ padding: "9px", background: loading.sweep ? "rgba(249,115,22,0.06)" : "rgba(249,115,22,0.10)", border: "1px solid rgba(249,115,22,0.3)", color: loading.sweep ? "rgba(249,115,22,0.3)" : "#f97316", fontSize: "9px", letterSpacing: "3px", cursor: loading.sweep ? "not-allowed" : "pointer", textTransform: "uppercase" }}>
              {loading.sweep ? "SWEEPING…" : "WALL CROSSING"}
            </button>
          </div>

          {error && (
            <div style={{ marginTop: "10px", padding: "8px", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.3)", fontSize: "8px", color: "#f87171", letterSpacing: "1px", wordBreak: "break-all" }}>
              ⚠ {error}
            </div>
          )}
        </aside>

        {/* Main */}
        <main style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
          {/* Stat row */}
          <div style={{ display: "flex", gap: "10px", padding: "14px 20px", flexWrap: "wrap", borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
            {runData ? <>
              <StatPill label="MESH nV/nE/nF" value={`${runData.mesh.nV}·${runData.mesh.nE}·${runData.mesh.nF}`} color="#4ee8d0" />
              {runData.slopes.map((s, i) => (
                <StatPill key={i} label={`SLOPE λ${i + 1}`} value={s.toFixed(5)} color={i === 0 ? "#4ee8d0" : "#f97316"} />
              ))}
              <StatPill label="GAUGE DIM" value={runData.gauge_algebra_dim} color="#c084fc" sub={`expected ${runData.expected_gauge_dim}`} />
              <StatPill label="ZERO MODES" value={runData.zero_modes} color="#facc15" />
              <StatPill label="AVG ‖F‖" value={runData.curv_mean.toFixed(5)} color="rgba(255,255,255,0.6)" />
            </> : (
              <div style={{ fontSize: "9px", color: "rgba(255,255,255,0.2)", letterSpacing: "2px", padding: "4px 0" }}>
                Press RUN SIMULATION to fetch full pipeline results from the FastAPI backend
              </div>
            )}
          </div>

          {/* Tabs */}
          <div style={{ display: "flex", borderBottom: "1px solid rgba(255,255,255,0.05)", padding: "0 20px" }}>
            {TABS.map(t => (
              <button key={t} onClick={() => setTab(t)} style={{ padding: "10px 18px", background: "none", border: "none", borderBottom: tab === t ? "2px solid #4ee8d0" : "2px solid transparent", color: tab === t ? "#4ee8d0" : "rgba(255,255,255,0.3)", fontSize: "9px", letterSpacing: "2px", cursor: "pointer", textTransform: "uppercase", marginBottom: "-1px" }}>
                {t}
              </button>
            ))}
          </div>

          {/* Canvas area */}
          <div style={{ flex: 1, padding: "20px", display: "flex", flexDirection: "column", gap: "12px" }}>
            {tab === "Curvature" && (
              <>
                <div style={{ fontSize: "8px", letterSpacing: "3px", color: "rgba(255,255,255,0.2)" }}>FACE CURVATURE NORMS ‖F_f‖ — {runData ? `${runData.mesh.nF} faces` : "awaiting data"}</div>
                <div style={{ flex: 1, background: "rgba(255,255,255,0.01)", border: "1px solid rgba(255,255,255,0.06)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  {!runData ? <span style={{ fontSize: "9px", color: "rgba(255,255,255,0.15)", letterSpacing: "3px" }}>RUN SIMULATION →</span>
                    : <canvas ref={heatRef} width={600} height={340} style={{ width: "100%", height: "auto" }} />}
                </div>
              </>
            )}
            {tab === "Wall-Crossing" && (
              <>
                <div style={{ fontSize: "8px", letterSpacing: "3px", color: "rgba(255,255,255,0.2)", display: "flex", gap: "16px" }}>
                  <span>SLOPE FILTRATION vs MIXING t</span>
                  <span style={{ color: "#4ee8d0" }}>── λ₁</span>
                  <span style={{ color: "#f97316" }}>── λ₂</span>
                </div>
                <div style={{ flex: 1, background: "rgba(255,255,255,0.01)", border: "1px solid rgba(255,255,255,0.06)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  {!sweepData ? <span style={{ fontSize: "9px", color: "rgba(255,255,255,0.15)", letterSpacing: "3px" }}>WALL CROSSING →</span>
                    : <canvas ref={lineRef} width={600} height={320} style={{ width: "100%", height: "auto" }} />}
                </div>
                {sweepData && <div style={{ fontSize: "8px", color: "rgba(255,255,255,0.15)", letterSpacing: "1px" }}>
                  Mesh {sweepData.mesh.nV}v · {sweepData.mesh.nE}e · {sweepData.mesh.nF}f — μ₁={sweepP.mu1} μ₂={sweepP.mu2} — {sweepP.steps} steps
                </div>}
              </>
            )}
            {tab === "Spectrum" && (
              <>
                <div style={{ fontSize: "8px", letterSpacing: "3px", color: "rgba(255,255,255,0.2)" }}>DOLBEAULT LAPLACIAN EIGENVALUES (FEEC, SPARSE EIGSH)</div>
                <div style={{ flex: 1, background: "rgba(255,255,255,0.01)", border: "1px solid rgba(255,255,255,0.06)", display: "flex", alignItems: "center", justifyContent: "center" }}>
                  {!runData ? <span style={{ fontSize: "9px", color: "rgba(255,255,255,0.15)", letterSpacing: "3px" }}>RUN SIMULATION →</span>
                    : <canvas ref={specRef} width={600} height={300} style={{ width: "100%", height: "auto" }} />}
                </div>
                {runData && <div style={{ fontSize: "8px", color: "rgba(255,255,255,0.15)", letterSpacing: "1px" }}>
                  {runData.zero_modes} zero mode(s) · threshold &lt; 1e-7 · {runData.dolbeault_eigenvalues.length} eigenvalues computed
                </div>}
              </>
            )}
            {tab === "Data" && runData && (
              <div style={{ fontSize: "10px", lineHeight: 2.2, overflowY: "auto" }}>
                <table style={{ borderCollapse: "collapse", width: "100%" }}>
                  <tbody>
                    {[
                      ["Vertices", runData.mesh.nV],
                      ["Edges", runData.mesh.nE],
                      ["Faces", runData.mesh.nF],
                      ["───", "─────────────────────"],
                      ...runData.slopes.map((s, i) => [`λ${i + 1} (slope)`, s.toExponential(8)]),
                      ["Δλ", (runData.slopes[0] - (runData.slopes[1] ?? 0)).toExponential(8)],
                      ["tr(Φ)", runData.phi_trace.toExponential(8)],
                      ["‖Φ‖", runData.phi_norm.toExponential(8)],
                      ["───", "─────────────────────"],
                      ["Gauge algebra dim", runData.gauge_algebra_dim],
                      ["Expected (u(N))", runData.expected_gauge_dim],
                      ["───", "─────────────────────"],
                      ["Mean ‖F‖", runData.curv_mean.toExponential(8)],
                      ["Max ‖F‖", runData.curv_max.toExponential(8)],
                      ["Zero modes (Δ)", runData.zero_modes],
                      ["───", "─────────────────────"],
                      ["Eigenvalues", runData.dolbeault_eigenvalues.map(v => v.toExponential(3)).join("  ")],
                    ].map(([k, v], i) => (
                      <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.03)" }}>
                        <td style={{ color: "rgba(255,255,255,0.3)", paddingRight: "28px", fontSize: "9px", letterSpacing: "2px" }}>{k}</td>
                        <td style={{ color: k.startsWith("─") ? "rgba(255,255,255,0.08)" : "#e2e8f0", fontSize: "11px" }}>{v}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            {tab === "Data" && !runData && (
              <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <span style={{ fontSize: "9px", color: "rgba(255,255,255,0.15)", letterSpacing: "3px" }}>RUN SIMULATION →</span>
              </div>
            )}
          </div>
        </main>
      </div>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=Space+Mono&display=swap'); *{box-sizing:border-box;}`}</style>
    </div>
  );
}
