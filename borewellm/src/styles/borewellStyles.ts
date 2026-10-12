export const appStyles = `
/* BorewellMart & GoogleBore Industrial Light Theme Styling */
:root {
  --navy: #0a2540;
  --navy-light: #13395e;
  --navy-dark: #061729;
  --blue: #0084ff;
  --cyan: #06b6d4;
  --amber: #f59e0b;
  --amber-dark: #d97706;
  --bg-porcelain: #f8fafc;
  --card-bg: #ffffff;
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #64748b;
  --border-light: rgba(15, 23, 42, 0.08);
  --border-focus: rgba(0, 132, 255, 0.35);
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 8px 24px rgba(10, 37, 64, 0.07), 0 2px 6px rgba(10, 37, 64, 0.04);
  --shadow-lg: 0 20px 35px -5px rgba(10, 37, 64, 0.12), 0 10px 15px -5px rgba(10, 37, 64, 0.05);
  --shadow-xl: 0 25px 50px -12px rgba(10, 37, 64, 0.2);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
  background-color: var(--bg-porcelain);
  color: var(--text-primary);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* Animations & Keyframes */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-8px);
  }
}

@keyframes radarPing {
  0% {
    transform: scale(0.9);
    opacity: 0.9;
  }
  50% {
    transform: scale(1.4);
    opacity: 0.3;
  }
  100% {
    transform: scale(1.9);
    opacity: 0;
  }
}

@keyframes marquee {
  0% {
    transform: translateX(0%);
  }
  100% {
    transform: translateX(-50%);
  }
}

@keyframes drillSpin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@keyframes waterPulse {
  0%, 100% {
    opacity: 0.6;
    transform: scale(1);
  }
  50% {
    opacity: 1;
    transform: scale(1.08);
  }
}

@keyframes bubbleRise {
  0% {
    transform: translateY(15px) scale(0.6);
    opacity: 0;
  }
  50% {
    opacity: 0.9;
  }
  100% {
    transform: translateY(-25px) scale(1.2);
    opacity: 0;
  }
}

@keyframes shimmer {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

@keyframes pulseGlow {
  0%, 100% {
    box-shadow: 0 0 15px rgba(37, 211, 102, 0.4);
  }
  50% {
    box-shadow: 0 0 30px rgba(37, 211, 102, 0.8), 0 0 10px rgba(37, 211, 102, 0.5);
  }
}

.float-anim {
  animation: float 4s ease-in-out infinite;
}

.float-anim-delay {
  animation: float 4.5s ease-in-out infinite;
  animation-delay: 1.5s;
}

/* Layout Utilities */
.container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Top Urgent 24x7 Helpline Bar */
.top-bar {
  background: var(--navy-dark);
  color: #ffffff;
  padding: 8px 16px;
  font-size: 13px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 50;
}

.top-bar-inner {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.beacon-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
}

.radar-beacon {
  position: relative;
  width: 12px;
  height: 12px;
}

.radar-core {
  width: 8px;
  height: 8px;
  background-color: #ef4444;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
}

.radar-wave {
  position: absolute;
  top: -2px;
  left: -2px;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: rgba(239, 68, 68, 0.5);
  animation: radarPing 2s infinite cubic-bezier(0, 0, 0.2, 1);
}

.phone-link {
  color: #38bdf8;
  font-weight: 700;
  text-decoration: none;
  font-family: 'JetBrains Mono', monospace;
  letter-spacing: 0.5px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 8px;
  border-radius: 4px;
  background: rgba(56, 189, 248, 0.1);
  transition: all 0.2s ease;
}

.phone-link:hover {
  background: rgba(56, 189, 248, 0.2);
  color: #ffffff;
}

/* Navbar */
.navbar {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 40;
  border-bottom: 1px solid var(--border-light);
  box-shadow: 0 4px 20px rgba(10, 37, 64, 0.04);
}

.nav-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}

.brand-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  cursor: pointer;
}

.brand-icon-box {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--navy) 0%, var(--blue) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(0, 132, 255, 0.3);
}

.brand-title {
  font-size: 20px;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -0.5px;
  line-height: 1.1;
}

.brand-sub {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--amber-dark);
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 28px;
}

.nav-item {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s ease;
  position: relative;
  cursor: pointer;
  background: none;
  border: none;
  padding: 0;
}

.nav-item:hover {
  color: var(--blue);
}

.btn-primary {
  background: linear-gradient(135deg, var(--navy) 0%, var(--blue) 100%);
  color: #ffffff;
  font-weight: 700;
  font-size: 14px;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(0, 132, 255, 0.3);
  transition: all 0.25s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 132, 255, 0.4);
}

.btn-outline {
  background: #ffffff;
  color: var(--navy);
  font-weight: 700;
  font-size: 14px;
  padding: 9px 18px;
  border-radius: 8px;
  border: 1.5px solid var(--border-light);
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-outline:hover {
  border-color: var(--navy);
  background: var(--bg-porcelain);
  color: var(--blue);
}

.btn-amber {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: #ffffff;
  font-weight: 700;
  font-size: 14px;
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(217, 119, 6, 0.35);
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-amber:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(217, 119, 6, 0.45);
}

/* Hero Section */
.hero-section {
  padding: 48px 0 64px 0;
  background: radial-gradient(circle at 85% 15%, rgba(6, 182, 212, 0.08) 0%, transparent 45%),
              radial-gradient(circle at 15% 85%, rgba(0, 132, 255, 0.05) 0%, transparent 40%),
              linear-gradient(180deg, #ffffff 0%, var(--bg-porcelain) 100%);
  border-bottom: 1px solid var(--border-light);
  position: relative;
  overflow: hidden;
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: start;
}

.hero-kicker {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--blue);
  margin-bottom: 16px;
}

.hero-kicker-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cyan);
}

.hero-heading {
  font-size: 46px;
  font-weight: 800;
  line-height: 1.15;
  color: var(--navy);
  letter-spacing: -1px;
  margin-bottom: 20px;
}

.hero-heading span {
  background: linear-gradient(135deg, var(--blue) 0%, var(--cyan) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  font-size: 17px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 28px;
}

/* Quick Search Card */
.search-card {
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 16px;
  box-shadow: var(--shadow-md);
  margin-bottom: 32px;
}

.search-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr auto;
  gap: 12px;
  align-items: center;
}

.search-field {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.search-label {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.search-select {
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 6px;
  border: 1px solid rgba(15, 23, 42, 0.15);
  background-color: #ffffff;
  color: var(--text-primary);
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
}

.search-select:focus {
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(0, 132, 255, 0.15);
}

.search-btn {
  height: 42px;
  align-self: flex-end;
  background: var(--navy);
  color: #ffffff;
  border: none;
  border-radius: 6px;
  padding: 0 20px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
  white-space: nowrap;
}

.search-btn:hover {
  background: var(--blue);
}

/* Trust Metric Badges */
.trust-metrics-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.trust-metric-card {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  padding: 14px;
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s ease;
}

.trust-metric-card:hover {
  transform: translateY(-3px);
}

.metric-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  font-weight: 800;
  color: var(--navy);
  line-height: 1.1;
}

.metric-label {
  font-size: 12px;
  color: var(--text-muted);
  font-weight: 500;
  margin-top: 4px;
}

/* Simulator / Live Estimation Card */
.calc-wrapper {
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  position: relative;
}

.calc-header {
  background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
  color: #ffffff;
  padding: 20px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.calc-title {
  font-size: 18px;
  font-weight: 800;
}

.calc-sub {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 500;
}

.calc-body {
  padding: 24px;
}

/* Geological Subterranean Visualizer */
.geo-visualizer {
  position: relative;
  height: 240px;
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(15, 23, 42, 0.15);
  margin-bottom: 20px;
  display: flex;
  box-shadow: inset 0 2px 8px rgba(0,0,0,0.2);
}

.strata-column {
  flex: 1;
  position: relative;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.strata-band {
  width: 100%;
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
  display: flex;
  align-items: center;
  padding: 0 16px;
}

.strata-label {
  font-size: 11px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  text-shadow: 0 1px 3px rgba(0,0,0,0.7);
  z-index: 2;
  letter-spacing: 0.5px;
}

/* Drill Pipe & Bit Animation inside Visualizer */
.drill-rig-surface {
  position: absolute;
  top: 0;
  left: 65%;
  transform: translateX(-50%);
  z-index: 10;
  width: 50px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.rig-surface-icon {
  width: 32px;
  height: 32px;
  background: var(--amber);
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0,0,0,0.3);
  margin-bottom: -4px;
  z-index: 12;
}

.drill-pipe {
  width: 8px;
  background: linear-gradient(90deg, #94a3b8 0%, #cbd5e1 50%, #64748b 100%);
  box-shadow: 0 0 6px rgba(0,0,0,0.4);
  transition: height 0.15s cubic-bezier(0.2, 0.8, 0.2, 1);
  position: relative;
}

.casing-pipe-overlay {
  position: absolute;
  top: 0;
  left: -2px;
  width: 12px;
  background: repeating-linear-gradient(
    0deg,
    #0284c7,
    #0284c7 6px,
    #0369a1 6px,
    #0369a1 12px
  );
  border-radius: 2px;
  opacity: 0.9;
  z-index: 11;
}

.drill-bit {
  position: absolute;
  bottom: -14px;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 15;
}

.drill-cutter {
  width: 16px;
  height: 12px;
  background: linear-gradient(180deg, #d97706, #78350f);
  clip-path: polygon(0 0, 100% 0, 50% 100%);
  animation: drillSpin 0.35s linear infinite;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}

.water-splash-zone {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 38%;
  background: radial-gradient(ellipse at bottom, rgba(6, 182, 212, 0.45) 0%, rgba(2, 132, 199, 0.2) 70%, transparent 100%);
  pointer-events: none;
  z-index: 5;
  animation: waterPulse 2s ease-in-out infinite;
}

.bubble {
  position: absolute;
  width: 6px;
  height: 6px;
  background: rgba(255, 255, 255, 0.85);
  border-radius: 50%;
  animation: bubbleRise 1.8s infinite ease-out;
}

/* Slider Controls */
.slider-container {
  margin: 16px 0 24px 0;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.slider-depth-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 26px;
  font-weight: 800;
  color: var(--blue);
}

.depth-slider {
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #e2e8f0;
  outline: none;
  -webkit-appearance: none;
  cursor: pointer;
}

.depth-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--blue);
  border: 3px solid #ffffff;
  box-shadow: 0 2px 8px rgba(0, 132, 255, 0.4);
  cursor: pointer;
  transition: transform 0.1s;
}

.depth-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}

/* Cost Breakdown Table */
.cost-breakdown-box {
  background: var(--bg-porcelain);
  border: 1px solid var(--border-light);
  border-radius: 10px;
  padding: 16px;
}

.cost-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  font-size: 13px;
  border-bottom: 1px dashed rgba(15, 23, 42, 0.1);
}

.cost-row:last-child {
  border-bottom: none;
  padding-top: 10px;
}

.cost-name {
  color: var(--text-secondary);
}

.cost-val {
  font-family: 'JetBrains Mono', monospace;
  font-weight: 700;
  color: var(--navy);
}

.cost-total-row {
  font-size: 16px;
  font-weight: 800;
  color: var(--navy);
}

.cost-total-val {
  font-family: 'JetBrains Mono', monospace;
  font-size: 22px;
  font-weight: 800;
  color: #0284c7;
}

/* Continuous Brand Marquee */
.marquee-section {
  padding: 24px 0;
  background: #ffffff;
  border-bottom: 1px solid var(--border-light);
  overflow: hidden;
}

.marquee-title {
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1.5px;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.marquee-track-wrap {
  width: 100%;
  overflow: hidden;
  display: flex;
  user-select: none;
}

.marquee-track {
  display: flex;
  gap: 36px;
  animation: marquee 26s linear infinite;
  min-width: 200%;
}

.marquee-track:hover {
  animation-play-state: paused;
}

.brand-chip {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-porcelain);
  border: 1px solid var(--border-light);
  padding: 8px 16px;
  border-radius: 8px;
  white-space: nowrap;
}

.brand-chip-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--navy);
}

.brand-chip-tag {
  font-size: 11px;
  color: var(--text-muted);
  padding-left: 6px;
  border-left: 1px solid rgba(15, 23, 42, 0.15);
}

/* Services Section */
.services-section {
  padding: 80px 0;
}

.section-head {
  text-align: center;
  max-width: 680px;
  margin: 0 auto 52px auto;
}

.section-kicker {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--blue);
  margin-bottom: 8px;
  display: inline-block;
}

.section-heading {
  font-size: 36px;
  font-weight: 800;
  color: var(--navy);
  letter-spacing: -0.5px;
  line-height: 1.2;
  margin-bottom: 14px;
}

.section-desc {
  font-size: 16px;
  color: var(--text-secondary);
}

.services-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 28px;
}

.service-card {
  background: #ffffff;
  border-radius: 14px;
  border: 1px solid var(--border-light);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
}

.service-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl);
  border-color: rgba(0, 132, 255, 0.25);
}

.service-img-wrap {
  width: 100%;
  height: 200px;
  overflow: hidden;
  position: relative;
}

.service-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.service-card:hover .service-img {
  transform: scale(1.06);
}

.service-content {
  padding: 24px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.service-kicker-text {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--amber-dark);
  margin-bottom: 6px;
}

.service-title {
  font-size: 18px;
  font-weight: 700;
  color: var(--navy);
  margin-bottom: 10px;
  line-height: 1.3;
}

.service-desc-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.55;
  margin-bottom: 16px;
  flex: 1;
}

.service-specs-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 18px;
}

.spec-item {
  font-size: 12px;
  color: var(--text-secondary);
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.service-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 14px;
  border-top: 1px solid var(--border-light);
}

.service-price {
  font-family: 'JetBrains Mono', monospace;
  font-size: 14px;
  font-weight: 700;
  color: var(--navy);
}

/* Vendor Package Card */
.vendor-section {
  padding: 72px 0;
  background: linear-gradient(180deg, var(--bg-porcelain) 0%, #ffffff 100%);
}

.vendor-card {
  background: radial-gradient(circle at 90% 10%, rgba(245, 158, 11, 0.15) 0%, transparent 40%),
              radial-gradient(circle at 10% 90%, rgba(0, 132, 255, 0.1) 0%, transparent 40%),
              linear-gradient(135deg, var(--navy-dark) 0%, var(--navy) 100%);
  border-radius: 20px;
  padding: 48px;
  color: #ffffff;
  box-shadow: var(--shadow-xl);
  border: 1px solid rgba(255, 255, 255, 0.12);
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 40px;
  align-items: center;
}

.vendor-kicker {
  color: #fcd34d;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  margin-bottom: 12px;
  display: inline-block;
}

.vendor-title {
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.5px;
  line-height: 1.2;
  margin-bottom: 16px;
}

.vendor-checklist {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin: 24px 0;
}

.vendor-check-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 14px;
  color: #e2e8f0;
}

.vendor-price-card {
  background: rgba(255, 255, 255, 0.07);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

.strikethrough-price {
  text-decoration: line-through;
  color: #94a3b8;
  font-size: 16px;
  font-family: 'JetBrains Mono', monospace;
}

.offer-price {
  font-family: 'JetBrains Mono', monospace;
  font-size: 44px;
  font-weight: 800;
  color: #38bdf8;
  margin: 6px 0;
}

.offer-tag {
  display: inline-block;
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 20px;
}

/* Regional Contractors Section */
.contractors-section {
  padding: 80px 0;
  background: #ffffff;
  border-bottom: 1px solid var(--border-light);
}

.contractors-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.contractor-card {
  background: var(--bg-porcelain);
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 22px;
  transition: all 0.25s ease;
  display: flex;
  flex-direction: column;
}

.contractor-card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-lg);
  border-color: rgba(0, 132, 255, 0.3);
  background: #ffffff;
}

.contractor-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.contractor-avatar {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--blue);
}

.contractor-name {
  font-size: 16px;
  font-weight: 700;
  color: var(--navy);
}

.contractor-enterprise {
  font-size: 13px;
  color: var(--text-secondary);
}

.contractor-location {
  font-size: 12px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 2px;
}

.rig-details-box {
  background: #ffffff;
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 16px;
  font-size: 12px;
}

.rig-detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.rig-detail-row:last-child {
  margin-bottom: 0;
}

.rig-key {
  color: var(--text-muted);
}

.rig-val {
  font-weight: 600;
  color: var(--text-primary);
}

.contractor-stats {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-top: 1px solid var(--border-light);
  border-bottom: 1px solid var(--border-light);
  margin-bottom: 16px;
}

.c-stat-box {
  text-align: center;
}

.c-stat-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 15px;
  font-weight: 800;
  color: var(--navy);
}

.c-stat-label {
  font-size: 11px;
  color: var(--text-muted);
}

/* FAQ Section */
.faq-section {
  padding: 80px 0;
  background: var(--bg-porcelain);
}

.faq-grid {
  max-width: 840px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.faq-card {
  background: #ffffff;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s ease;
}

.faq-card:hover {
  border-color: rgba(0, 132, 255, 0.3);
}

.faq-question-btn {
  width: 100%;
  padding: 20px 24px;
  text-align: left;
  background: none;
  border: none;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
  font-weight: 700;
  color: var(--navy);
  cursor: pointer;
}

.faq-answer {
  padding: 0 24px 20px 24px;
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Footer */
.site-footer {
  background: var(--navy-dark);
  color: #94a3b8;
  padding: 64px 0 32px 0;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 13px;
}

.footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
  margin-bottom: 48px;
}

.footer-col-title {
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 16px;
}

.footer-links-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  list-style: none;
}

.footer-link {
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.2s;
  cursor: pointer;
}

.footer-link:hover {
  color: #38bdf8;
}

.footer-bottom {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

/* Modal Styling */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(10, 37, 64, 0.65);
  backdrop-filter: blur(6px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-card {
  background: #ffffff;
  border-radius: 16px;
  width: 100%;
  max-width: 540px;
  box-shadow: var(--shadow-xl);
  overflow: hidden;
  border: 1px solid var(--border-light);
  animation: float 0.3s ease-out;
}

.modal-header {
  background: var(--navy);
  color: #ffffff;
  padding: 20px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
}

.modal-close-btn {
  background: none;
  border: none;
  color: #cbd5e1;
  font-size: 22px;
  cursor: pointer;
  line-height: 1;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid rgba(15, 23, 42, 0.15);
  font-size: 14px;
  outline: none;
  font-family: inherit;
}

.form-input:focus {
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(0, 132, 255, 0.15);
}

/* Floating WhatsApp / SOS Action */
.sos-floating-wrap {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 90;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.sos-btn {
  background: #25d366;
  color: #ffffff;
  border: none;
  border-radius: 50px;
  padding: 12px 22px;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(37, 211, 102, 0.4);
  animation: pulseGlow 2.5s infinite;
  text-decoration: none;
  transition: transform 0.2s;
}

.sos-btn:hover {
  transform: scale(1.05);
}

/* Toast Message */
.toast-notice {
  position: fixed;
  top: 24px;
  right: 24px;
  background: #0f172a;
  color: #ffffff;
  padding: 14px 22px;
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.3);
  z-index: 110;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  border-left: 4px solid #10b981;
}

/* Responsive Styles */
@media (max-width: 1024px) {
  .hero-grid {
    grid-template-columns: 1fr;
  }
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .contractors-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .vendor-card {
    grid-template-columns: 1fr;
  }
  .footer-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .hero-heading {
    font-size: 32px;
  }
  .search-grid {
    grid-template-columns: 1fr;
  }
  .services-grid {
    grid-template-columns: 1fr;
  }
  .contractors-grid {
    grid-template-columns: 1fr;
  }
  .nav-links {
    display: none;
  }
  .trust-metrics-grid {
    grid-template-columns: 1fr;
  }
  .footer-grid {
    grid-template-columns: 1fr;
  }
}
`;
