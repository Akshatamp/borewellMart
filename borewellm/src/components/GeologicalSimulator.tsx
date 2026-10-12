import React, { useMemo } from 'react';
import { GEOLOGICAL_STRATA } from '../data/borewellData';

interface GeologicalSimulatorProps {
  depth: number;
  setDepth: (depth: number) => void;
  onBookNow: (depth: number) => void;
}

export const GeologicalSimulator: React.FC<GeologicalSimulatorProps> = ({
  depth,
  setDepth,
  onBookNow
}) => {
  // Current stratum based on depth
  const currentStratum = useMemo(() => {
    return (
      GEOLOGICAL_STRATA.find(
        (s) => depth >= s.depthMin && depth <= s.depthMax
      ) || GEOLOGICAL_STRATA[GEOLOGICAL_STRATA.length - 1]
    );
  }, [depth]);

  const isAquiferReached = depth >= 500;

  // Pipe height in % relative to visualizer container (min 15%, max 92%)
  const pipeHeightPercent = useMemo(() => {
    const minD = 150;
    const maxD = 1200;
    const pct = ((depth - minD) / (maxD - minD)) * 75 + 15;
    return Math.min(Math.max(pct, 15), 90);
  }, [depth]);

  // Cost estimates
  const costBreakdown = useMemo(() => {
    const rigSetup = 5000;
    const drillingRate = depth > 700 ? 105 : 95;
    const drillingCost = depth * drillingRate;
    const casingFeet = Math.min(depth, 85);
    const casingCost = casingFeet * 380; // Class-V heavy PVC casing
    const compressorFlushing = 4500;
    const total = rigSetup + drillingCost + casingCost + compressorFlushing;

    return {
      rigSetup,
      drillingRate,
      drillingCost,
      casingFeet,
      casingCost,
      compressorFlushing,
      total
    };
  }, [depth]);

  return (
    <div className="calc-wrapper">
      <div className="calc-header">
        <div>
          <div className="calc-title">Subterranean Geological Simulator</div>
          <div className="calc-sub">Interactive Sub-Surface Strata & Real-Time Cost Estimator</div>
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#93c5fd', fontWeight: 700 }}>
            Target Formation
          </div>
          <div style={{ fontSize: '13px', fontWeight: 700, color: '#38bdf8' }}>
            {isAquiferReached ? '🌊 Confined Aquifer' : '⛏️ Fractured Bedrock'}
          </div>
        </div>
      </div>

      <div className="calc-body">
        {/* Visual cross-section */}
        <div className="geo-visualizer">
          {/* Strata layers */}
          <div className="strata-column">
            {GEOLOGICAL_STRATA.map((stratum, idx) => {
              const heightPct = idx === 0 ? '16%' : idx === 1 ? '24%' : idx === 2 ? '28%' : '32%';
              return (
                <div
                  key={stratum.name}
                  className="strata-band"
                  style={{
                    height: heightPct,
                    background: stratum.texture,
                    borderBottom: '1px solid rgba(255,255,255,0.1)'
                  }}
                >
                  <span className="strata-label">
                    {idx + 1}. {stratum.name} ({stratum.depthMin}-{stratum.depthMax} ft)
                  </span>
                </div>
              );
            })}
          </div>

          {/* Drill Rig & Animated Pipe */}
          <div className="drill-rig-surface" style={{ height: `${pipeHeightPercent}%` }}>
            <div className="rig-surface-icon" title="DTH Hydraulic Rotary Rig">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="12 2 2 22 22 22 12 2" />
                <line x1="12" y1="12" x2="12" y2="18" />
              </svg>
            </div>

            <div className="drill-pipe" style={{ height: '100%' }}>
              {/* Blue outer casing sleeve for first 85ft */}
              <div
                className="casing-pipe-overlay"
                style={{ height: `${Math.min(100, (85 / depth) * 100)}%` }}
                title="Schedule-40 / Class-V Surface Casing Pipe"
              />

              {/* Spinning cutter bit at bottom */}
              <div className="drill-bit">
                <div className="drill-cutter" />
              </div>
            </div>
          </div>

          {/* Aquifer splash and bubbles when depth >= 500 */}
          {isAquiferReached && (
            <div className="water-splash-zone">
              <div className="bubble" style={{ left: '20%', bottom: '10px', animationDelay: '0s' }} />
              <div className="bubble" style={{ left: '55%', bottom: '25px', animationDelay: '0.4s' }} />
              <div className="bubble" style={{ left: '75%', bottom: '15px', animationDelay: '0.9s' }} />
              <div className="bubble" style={{ left: '40%', bottom: '40px', animationDelay: '1.2s' }} />
              <div
                style={{
                  position: 'absolute',
                  bottom: '12px',
                  right: '16px',
                  background: 'rgba(6, 182, 212, 0.95)',
                  color: '#ffffff',
                  padding: '4px 10px',
                  borderRadius: '6px',
                  fontSize: '11px',
                  fontWeight: 800,
                  boxShadow: '0 2px 8px rgba(0,0,0,0.3)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <span>💦 HIGH WATER DISCHARGE STRUCK</span>
              </div>
            </div>
          )}
        </div>

        {/* Depth Slider */}
        <div className="slider-container">
          <div className="slider-labels">
            <div>
              <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>Calculated Depth:</span>
              <div className="slider-depth-num">{depth} <span style={{ fontSize: '15px', color: '#64748b' }}>Feet</span></div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 600 }}>Active Strata:</span>
              <div style={{ fontSize: '13px', fontWeight: 700, color: '#0a2540' }}>{currentStratum.name}</div>
            </div>
          </div>

          <input
            type="range"
            min="150"
            max="1200"
            step="10"
            value={depth}
            onChange={(e) => setDepth(Number(e.target.value))}
            className="depth-slider"
          />

          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#94a3b8', marginTop: '6px', fontFamily: 'JetBrains Mono' }}>
            <span>150 ft (Shallow)</span>
            <span>500 ft (Aquifer Zone)</span>
            <span>800 ft (Deep)</span>
            <span>1200 ft (Ultra Deep)</span>
          </div>
        </div>

        {/* Current layer insight */}
        <div style={{ background: '#f1f5f9', borderLeft: '3px solid #0084ff', padding: '10px 14px', borderRadius: '4px', fontSize: '12px', color: '#334155', marginBottom: '18px' }}>
          <strong>Layer Insight:</strong> {currentStratum.description}
          <div style={{ marginTop: '4px', display: 'flex', gap: '16px', color: '#0369a1', fontWeight: 600 }}>
            <span>Water Potential: {currentStratum.waterLikelihood}</span>
            <span>Casing: {currentStratum.casingRequired}</span>
          </div>
        </div>

        {/* Real-time cost estimation */}
        <div className="cost-breakdown-box">
          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.8px', color: '#64748b', marginBottom: '8px' }}>
            Transparent Government/Standard Rate Estimate
          </div>
          
          <div className="cost-row">
            <span className="cost-name">Heavy Rig Mobilization & Hydraulic Setup</span>
            <span className="cost-val">₹{costBreakdown.rigSetup.toLocaleString('en-IN')}</span>
          </div>

          <div className="cost-row">
            <span className="cost-name">DTH Drilling ({depth} ft @ ₹{costBreakdown.drillingRate}/ft)</span>
            <span className="cost-val">₹{costBreakdown.drillingCost.toLocaleString('en-IN')}</span>
          </div>

          <div className="cost-row">
            <span className="cost-name">Class-V Heavy PVC Casing ({costBreakdown.casingFeet} ft @ ₹380/ft)</span>
            <span className="cost-val">₹{costBreakdown.casingCost.toLocaleString('en-IN')}</span>
          </div>

          <div className="cost-row">
            <span className="cost-name">1200 CFM Compressor Flushing & Slit Extraction</span>
            <span className="cost-val">₹{costBreakdown.compressorFlushing.toLocaleString('en-IN')}</span>
          </div>

          <div className="cost-row cost-total-row">
            <span>Estimated Drilling Package</span>
            <span className="cost-total-val">₹{costBreakdown.total.toLocaleString('en-IN')}*</span>
          </div>
        </div>

        <div style={{ marginTop: '16px', display: 'flex', gap: '12px' }}>
          <button
            onClick={() => onBookNow(depth)}
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', padding: '12px 20px', fontSize: '15px' }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
            Lock This Rate & Book Survey ({depth} ft)
          </button>
        </div>
        <div style={{ fontSize: '11px', color: '#94a3b8', textAlign: 'center', marginTop: '8px' }}>
          *Excludes optional submersible pump set & electrical wiring. Free re-survey if water strikes below threshold.
        </div>
      </div>
    </div>
  );
};
