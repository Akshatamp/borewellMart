import React, { useState, useMemo } from 'react';

const cssStyles = `
  :root {
    --primary: #0284c7;
    --primary-dark: #0369a1;
    --primary-light: #e0f2fe;
    --primary-glow: rgba(2, 132, 199, 0.28);
    --secondary: #0f172a;
    --accent: #10b981;
    --accent-hover: #059669;
    --amber: #f59e0b;
    --text-main: #0f172a;
    --text-muted: #64748b;
    --bg-page: #f8fafc;
    --bg-white: #ffffff;
    --border-color: #e2e8f0;
    --border-light: #f1f5f9;
    --shadow-soft: 0 4px 20px -2px rgba(15, 23, 42, 0.06);
    --shadow-hover: 0 20px 35px -10px rgba(2, 132, 199, 0.18);
    --shadow-elevated: 0 25px 50px -12px rgba(15, 23, 42, 0.16);
    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 24px;
    --radius-full: 9999px;
    --font: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: var(--font);
    background-color: var(--bg-page);
    color: var(--text-main);
    line-height: 1.6;
    overflow-x: hidden;
    -webkit-font-smoothing: antialiased;
  }

  a {
    color: inherit;
    text-decoration: none;
  }

  button {
    cursor: pointer;
    font-family: inherit;
    border: none;
    outline: none;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* === Expansive Wide Container Architecture === */
  .container {
    width: 94%;
    max-width: 1560px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  .container-wide {
    width: 96%;
    max-width: 1680px;
    margin: 0 auto;
    padding: 0 1rem;
  }

  /* === Keyframe Animations === */
  @keyframes floatSlow {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    50% { transform: translateY(-8px) rotate(0.5deg); }
  }

  @keyframes floatReverse {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(8px); }
  }

  @keyframes pulseGlow {
    0%, 100% { transform: scale(1); opacity: 0.9; }
    50% { transform: scale(1.12); opacity: 0.35; }
  }

  @keyframes marquee {
    0% { transform: translateX(0); }
    100% { transform: translateX(-50%); }
  }

  @keyframes ripple {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }
    70% { box-shadow: 0 0 0 18px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
  }

  @keyframes drillSpin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }

  /* === Top Emergency Alert Bar (Full Bleed) === */
  .top-banner {
    background: linear-gradient(90deg, #075985 0%, #0369a1 40%, #0c4a6e 100%);
    color: #e0f2fe;
    font-size: 0.88rem;
    padding: 0.75rem 0;
    position: relative;
    z-index: 60;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  }

  .top-banner-inner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
  }

  .beacon-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    background: rgba(255, 255, 255, 0.18);
    padding: 0.3rem 0.85rem;
    border-radius: var(--radius-full);
    font-weight: 700;
    letter-spacing: 0.5px;
  }

  .pulse-dot {
    width: 9px;
    height: 9px;
    background-color: #34d399;
    border-radius: 50%;
    position: relative;
  }

  .pulse-dot::after {
    content: '';
    position: absolute;
    inset: -3px;
    border-radius: 50%;
    background-color: #34d399;
    animation: pulseGlow 1.5s infinite;
  }

  /* === Wide Navbar === */
  .navbar-wrapper {
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(226, 232, 240, 0.85);
    position: sticky;
    top: 0;
    z-index: 100;
    transition: all 0.3s;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.03);
  }

  .navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 82px;
  }

  .logo-block {
    display: flex;
    align-items: center;
    gap: 0.9rem;
    cursor: pointer;
  }

  .logo-icon-box {
    width: 48px;
    height: 48px;
    border-radius: var(--radius-md);
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    box-shadow: 0 6px 18px rgba(2, 132, 199, 0.4);
  }

  .brand-text h1 {
    font-size: 1.55rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #0f172a;
    line-height: 1;
  }

  .brand-text span {
    color: var(--primary);
  }

  .brand-sub {
    font-size: 0.74rem;
    font-weight: 700;
    color: var(--text-muted);
    letter-spacing: 0.6px;
    text-transform: uppercase;
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 2.5rem;
    list-style: none;
  }

  .nav-link {
    font-size: 1rem;
    font-weight: 600;
    color: #334155;
    position: relative;
    transition: color 0.2s;
  }

  .nav-link:hover {
    color: var(--primary);
  }

  .nav-actions {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  /* === Universal Buttons === */
  .btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    padding: 0.75rem 1.6rem;
    border-radius: var(--radius-sm);
    font-size: 0.95rem;
    font-weight: 700;
  }

  .btn-outline {
    background: #ffffff;
    color: var(--primary);
    border: 1.8px solid var(--primary);
  }

  .btn-outline:hover {
    background: var(--primary-light);
    transform: translateY(-2px);
  }

  .btn-primary {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35);
  }

  .btn-primary:hover {
    background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
    box-shadow: 0 8px 22px rgba(2, 132, 199, 0.45);
    transform: translateY(-2px);
  }

  .btn-accent {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: #ffffff;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
  }

  .btn-accent:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.45);
  }

  .btn-glow {
    position: relative;
    overflow: hidden;
  }

  .btn-glow::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 60%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
    transform: skewX(-25deg);
    transition: 0.75s;
  }

  .btn-glow:hover::before {
    left: 140%;
  }

  /* === Expansive Wide Hero Section === */
  .hero-section {
    position: relative;
    padding: 4.5rem 0 5.5rem;
    background: radial-gradient(circle at 85% 15%, #e0f2fe 0%, #f0f9ff 40%, #ffffff 80%);
    overflow: hidden;
    border-bottom: 1px solid var(--border-color);
  }

  .hero-grid {
    display: grid;
    grid-template-columns: 1.25fr 0.95fr;
    gap: 4.5rem;
    align-items: center;
  }

  .badge-tag-hero {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    background: #e0f2fe;
    color: #0369a1;
    font-size: 0.88rem;
    font-weight: 700;
    padding: 0.45rem 1.15rem;
    border-radius: var(--radius-full);
    border: 1px solid #bae6fd;
    margin-bottom: 1.5rem;
  }

  .hero-title {
    font-size: 3.85rem;
    line-height: 1.12;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.03em;
    margin-bottom: 1.5rem;
  }

  .hero-title .text-gradient {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .hero-desc {
    font-size: 1.22rem;
    color: var(--text-muted);
    line-height: 1.68;
    margin-bottom: 2.25rem;
    max-width: 780px;
  }

  /* Hero Wide Search & Filter Bar */
  .hero-search-box {
    background: #ffffff;
    border: 1.5px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.5rem;
    box-shadow: var(--shadow-hover);
    margin-top: 2rem;
  }

  .filter-grid {
    display: grid;
    grid-template-columns: 1.2fr 1.2fr 1.5fr auto;
    gap: 1.1rem;
    align-items: flex-end;
  }

  .field-group {
    display: flex;
    flex-direction: column;
    gap: 0.45rem;
  }

  .field-label {
    font-size: 0.78rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.6px;
  }

  .field-input {
    width: 100%;
    padding: 0.8rem 1rem;
    border-radius: var(--radius-sm);
    border: 1.5px solid var(--border-color);
    background: #f8fafc;
    font-size: 0.95rem;
    font-weight: 600;
    color: #1e293b;
    transition: all 0.2s;
  }

  .field-input:focus {
    background: #ffffff;
    border-color: var(--primary);
    box-shadow: 0 0 0 3px var(--primary-glow);
    outline: none;
  }

  /* Wide Hero Visual Montage */
  .hero-visual-wrapper {
    position: relative;
    display: flex;
    justify-content: center;
  }

  .hero-image-card {
    position: relative;
    width: 100%;
    max-width: 580px;
    height: 520px;
    border-radius: var(--radius-lg);
    overflow: hidden;
    box-shadow: var(--shadow-elevated);
    border: 6px solid #ffffff;
  }

  .hero-image-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .hero-image-card:hover img {
    transform: scale(1.05);
  }

  /* Floating Overlay Badges */
  .floating-badge {
    position: absolute;
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(226, 232, 240, 0.95);
    padding: 1rem 1.35rem;
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-hover);
    display: flex;
    align-items: center;
    gap: 0.9rem;
    z-index: 10;
  }

  .badge-one {
    top: 30px;
    left: -30px;
    animation: floatSlow 4.5s ease-in-out infinite;
  }

  .badge-two {
    bottom: 35px;
    right: -25px;
    animation: floatReverse 5s ease-in-out infinite;
  }

  .badge-icon-box {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .badge-title {
    font-size: 1.05rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.1;
  }

  .badge-subtitle {
    font-size: 0.78rem;
    color: var(--text-muted);
    font-weight: 600;
  }

  /* === Full Bleed Brand Ticker === */
  .ticker-wrap {
    background: #ffffff;
    border-top: 1px solid var(--border-color);
    border-bottom: 1px solid var(--border-color);
    padding: 1.6rem 0;
    overflow: hidden;
    position: relative;
  }

  .ticker-title {
    text-align: center;
    font-size: 0.8rem;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1rem;
  }

  .ticker-marquee {
    display: flex;
    width: 200%;
    animation: marquee 26s linear infinite;
  }

  .ticker-marquee:hover {
    animation-play-state: paused;
  }

  .brand-logo-item {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 0 3.25rem;
    font-size: 1.25rem;
    font-weight: 800;
    color: #475569;
    white-space: nowrap;
    opacity: 0.8;
    transition: opacity 0.2s;
  }

  .brand-logo-item:hover {
    opacity: 1;
    color: var(--primary);
  }

  /* === Universal Wide Sections === */
  .section {
    padding: 6.5rem 0;
  }

  .section-alt {
    background: #ffffff;
    border-top: 1px solid var(--border-color);
    border-bottom: 1px solid var(--border-color);
  }

  .section-head {
    text-align: center;
    max-width: 860px;
    margin: 0 auto 4rem;
  }

  .pill-badge {
    display: inline-block;
    color: var(--primary);
    background: var(--primary-light);
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    padding: 0.4rem 1rem;
    border-radius: var(--radius-full);
    margin-bottom: 0.9rem;
  }

  .section-title {
    font-size: 2.85rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.025em;
    margin-bottom: 0.9rem;
    line-height: 1.2;
  }

  .section-desc {
    font-size: 1.15rem;
    color: var(--text-muted);
    line-height: 1.6;
  }

  /* === Wide Interactive Depth Simulator & Estimator Dashboard === */
  .estimator-card {
    background: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-elevated);
    overflow: hidden;
  }

  .estimator-grid {
    display: grid;
    grid-template-columns: 380px 1.35fr 1fr;
  }

  /* Subterranean Geological Cross-Section Visualizer */
  .subsurface-visualizer {
    background: #0b1322;
    padding: 2.5rem 2rem;
    color: white;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    border-right: 1px solid rgba(255, 255, 255, 0.1);
  }

  .subsurface-title {
    font-size: 0.9rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    color: #38bdf8;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .rock-column {
    position: relative;
    height: 440px;
    border-radius: var(--radius-md);
    overflow: hidden;
    border: 2px solid rgba(255, 255, 255, 0.18);
    background: #1e293b;
    display: flex;
    flex-direction: column;
    box-shadow: inset 0 2px 12px rgba(0, 0, 0, 0.5);
  }

  .layer-topsoil {
    height: 25%;
    background: linear-gradient(180deg, #78350f 0%, #451a03 100%);
    padding: 0.65rem 0.85rem;
    font-size: 0.76rem;
    font-weight: 700;
    color: #fde68a;
    border-bottom: 1px dashed rgba(255, 255, 255, 0.25);
  }

  .layer-weathered {
    height: 30%;
    background: linear-gradient(180deg, #334155 0%, #1e293b 100%);
    padding: 0.65rem 0.85rem;
    font-size: 0.76rem;
    font-weight: 700;
    color: #cbd5e1;
    border-bottom: 1px dashed rgba(255, 255, 255, 0.25);
  }

  .layer-bedrock {
    height: 45%;
    background: linear-gradient(180deg, #090d16 0%, #0369a1 100%);
    padding: 0.65rem 0.85rem;
    font-size: 0.76rem;
    font-weight: 700;
    color: #38bdf8;
    position: relative;
  }

  /* Animated Rig Drill Pipe */
  .drill-rod {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 8px;
    background: repeating-linear-gradient(
      0deg,
      #94a3b8,
      #94a3b8 10px,
      #475569 10px,
      #475569 20px
    );
    transition: height 0.25s ease-out;
    z-index: 5;
    box-shadow: 0 0 8px rgba(0,0,0,0.5);
  }

  .drill-bit {
    position: absolute;
    bottom: -12px;
    left: 50%;
    transform: translateX(-50%);
    width: 22px;
    height: 20px;
    background: #f59e0b;
    border-radius: 2px 2px 10px 10px;
    box-shadow: 0 0 16px #f59e0b;
    animation: drillSpin 0.35s linear infinite;
  }

  .water-strike-zone {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 70px;
    background: rgba(2, 132, 199, 0.6);
    border-top: 2px solid #38bdf8;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.82rem;
    font-weight: 800;
    color: #e0f2fe;
    backdrop-filter: blur(3px);
  }

  /* Estimator Controls & Inputs */
  .estimator-inputs {
    padding: 3rem 2.5rem;
    border-right: 1px solid var(--border-color);
  }

  .range-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 0.85rem;
  }

  .depth-badge {
    font-size: 1.85rem;
    font-weight: 800;
    color: var(--primary);
    font-family: 'JetBrains Mono', monospace;
  }

  .range-slider {
    width: 100%;
    height: 12px;
    border-radius: 6px;
    background: #e2e8f0;
    outline: none;
    -webkit-appearance: none;
    margin-bottom: 2rem;
  }

  .range-slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: var(--primary);
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(2, 132, 199, 0.5);
    border: 3.5px solid #ffffff;
    transition: transform 0.15s;
  }

  .range-slider::-webkit-slider-thumb:hover {
    transform: scale(1.15);
  }

  .pill-options {
    display: flex;
    gap: 0.65rem;
    flex-wrap: wrap;
    margin-bottom: 1.75rem;
  }

  .pill-option {
    padding: 0.65rem 1.2rem;
    border-radius: var(--radius-sm);
    font-size: 0.92rem;
    font-weight: 700;
    background: #f1f5f9;
    color: #475569;
    border: 1.5px solid transparent;
    transition: all 0.2s;
  }

  .pill-option.active {
    background: var(--primary-light);
    color: var(--primary-dark);
    border-color: var(--primary);
  }

  /* Estimator Summary Pane */
  .estimator-summary {
    background: #f8fafc;
    padding: 3rem 2.25rem;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }

  .price-calc-box {
    background: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 1.85rem;
    margin-bottom: 1.75rem;
    box-shadow: var(--shadow-soft);
  }

  .calc-line {
    display: flex;
    justify-content: space-between;
    padding: 0.8rem 0;
    font-size: 0.95rem;
    color: #475569;
    border-bottom: 1px dashed var(--border-color);
  }

  .calc-line strong {
    color: #0f172a;
    font-family: 'JetBrains Mono', monospace;
  }

  .calc-total {
    margin-top: 1.25rem;
    display: flex;
    justify-content: space-between;
    align-items: baseline;
  }

  .calc-price {
    font-size: 2.35rem;
    font-weight: 800;
    color: var(--accent);
    font-family: 'JetBrains Mono', monospace;
  }

  /* === Expansive Wide Core Services Grid === */
  .services-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2.25rem;
  }

  .service-card {
    background: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    overflow: hidden;
    box-shadow: var(--shadow-soft);
    display: flex;
    flex-direction: column;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .service-card:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-hover);
    border-color: #cbd5e1;
  }

  .service-thumb {
    position: relative;
    height: 230px;
    overflow: hidden;
  }

  .service-thumb img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
  }

  .service-card:hover .service-thumb img {
    transform: scale(1.08);
  }

  .service-tag {
    position: absolute;
    top: 14px;
    right: 14px;
    background: rgba(15, 23, 42, 0.88);
    backdrop-filter: blur(8px);
    color: white;
    font-size: 0.76rem;
    font-weight: 700;
    padding: 0.3rem 0.75rem;
    border-radius: var(--radius-full);
  }

  .service-body {
    padding: 1.75rem;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
    justify-content: space-between;
  }

  .service-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 0.65rem;
    line-height: 1.3;
  }

  .service-desc {
    font-size: 0.98rem;
    color: var(--text-muted);
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }

  .service-bottom {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top: 1px solid var(--border-light);
    padding-top: 1.25rem;
  }

  .service-cost-tag {
    font-size: 0.9rem;
    font-weight: 700;
    color: #475569;
  }

  .service-cost-tag span {
    font-size: 1.25rem;
    color: var(--accent);
    font-weight: 800;
  }

  /* === Expansive Wide Vendor Growth Section === */
  .vendor-section {
    background: linear-gradient(135deg, #075985 0%, #0c4a6e 50%, #0f172a 100%);
    border-radius: var(--radius-lg);
    padding: 4.5rem 4rem;
    color: white;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-elevated);
  }

  .vendor-grid {
    display: grid;
    grid-template-columns: 1.35fr 0.9fr;
    gap: 4.5rem;
    align-items: center;
    position: relative;
    z-index: 10;
  }

  .offer-badge {
    background: #f59e0b;
    color: #000;
    font-size: 0.8rem;
    font-weight: 800;
    padding: 0.4rem 1rem;
    border-radius: var(--radius-full);
    text-transform: uppercase;
    display: inline-block;
    margin-bottom: 1.25rem;
    letter-spacing: 0.5px;
  }

  .vendor-title {
    font-size: 2.75rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 1.25rem;
  }

  .vendor-checklist {
    list-style: none;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.1rem;
    margin: 2.25rem 0;
  }

  .vendor-check-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1rem;
    font-weight: 600;
  }

  .pricing-glass-card {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    border: 1.5px solid rgba(255, 255, 255, 0.22);
    border-radius: var(--radius-md);
    padding: 3rem 2.5rem;
    text-align: center;
  }

  .strikethrough-tag {
    text-decoration: line-through;
    color: #94a3b8;
    font-size: 1.35rem;
  }

  .deal-price {
    font-size: 4.5rem;
    font-weight: 900;
    color: #38bdf8;
    line-height: 1;
    margin: 0.5rem 0;
    font-family: 'JetBrains Mono', monospace;
  }

  /* === Expansive Verified Contractor Cards === */
  .providers-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2.25rem;
  }

  .provider-card {
    background: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: 2.25rem;
    box-shadow: var(--shadow-soft);
    transition: all 0.3s;
  }

  .provider-card:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-hover);
  }

  .provider-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 1.15rem;
  }

  .provider-name {
    font-size: 1.25rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.25;
  }

  .provider-city {
    font-size: 0.9rem;
    color: var(--text-muted);
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.35rem;
    margin-top: 0.3rem;
  }

  .badge-verified-pro {
    background: #dcfce7;
    color: #15803d;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 0.3rem 0.65rem;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 0.35rem;
  }

  .provider-rating-row {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 1rem 0;
  }

  .stars {
    color: #f59e0b;
    font-weight: 800;
    font-size: 1.05rem;
  }

  .review-count {
    font-size: 0.88rem;
    color: var(--text-muted);
  }

  /* === Wide FAQ Accordion === */
  .faq-wrapper {
    max-width: 1040px;
    margin: 0 auto;
  }

  .faq-accordion-item {
    background: #ffffff;
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    margin-bottom: 1rem;
    overflow: hidden;
  }

  .faq-btn {
    width: 100%;
    padding: 1.5rem 1.85rem;
    text-align: left;
    background: none;
    font-size: 1.15rem;
    font-weight: 700;
    color: #0f172a;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .faq-btn:hover {
    background: #f8fafc;
  }

  .faq-text {
    padding: 0 1.85rem 1.5rem;
    font-size: 1.02rem;
    color: var(--text-muted);
    line-height: 1.65;
  }

  /* === Floating Emergency Call / WhatsApp Widget === */
  .floating-quick-action {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 99;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    align-items: flex-end;
  }

  .whatsapp-pulse-btn {
    background: #25d366;
    color: white;
    width: 62px;
    height: 62px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 6px 22px rgba(37, 211, 102, 0.45);
    animation: ripple 2s infinite;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .whatsapp-pulse-btn:hover {
    transform: scale(1.1);
  }

  /* === Modal Dialog === */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(6px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 1.5rem;
    z-index: 1000;
  }

  .modal-container {
    background: #ffffff;
    border-radius: var(--radius-lg);
    max-width: 540px;
    width: 100%;
    padding: 2.5rem;
    box-shadow: var(--shadow-elevated);
    position: relative;
    border: 1px solid var(--border-color);
  }

  .modal-close-btn {
    position: absolute;
    top: 1.25rem;
    right: 1.25rem;
    background: none;
    font-size: 1.5rem;
    color: #94a3b8;
  }

  .modal-close-btn:hover {
    color: #0f172a;
  }

  /* === Wide Footer === */
  .site-footer {
    background: #0f172a;
    color: #94a3b8;
    padding: 6rem 0 3rem;
  }

  .footer-columns {
    display: grid;
    grid-template-columns: 2.2fr 1fr 1fr 1.4fr;
    gap: 4rem;
    margin-bottom: 4rem;
  }

  .footer-heading {
    color: #ffffff;
    font-size: 1.15rem;
    font-weight: 800;
    margin-bottom: 1.4rem;
  }

  .footer-links {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    font-size: 0.96rem;
  }

  .footer-links a:hover {
    color: #38bdf8;
  }

  .footer-bottom-bar {
    border-top: 1px solid #1e293b;
    padding-top: 2.25rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 1.25rem;
    font-size: 0.9rem;
  }

  /* === Responsive Media Queries === */
  @media (max-width: 1200px) {
    .hero-grid {
      grid-template-columns: 1fr;
      text-align: center;
    }
    .hero-desc {
      margin: 0 auto 2.25rem;
    }
    .badge-tag-hero {
      margin: 0 auto 1.5rem;
    }
    .filter-grid {
      grid-template-columns: 1fr 1fr;
    }
    .estimator-grid {
      grid-template-columns: 1fr;
    }
    .subsurface-visualizer {
      border-right: none;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }
    .services-grid, .providers-grid {
      grid-template-columns: repeat(2, 1fr);
    }
    .vendor-grid {
      grid-template-columns: 1fr;
    }
    .footer-columns {
      grid-template-columns: 1fr 1fr;
    }
  }

  @media (max-width: 768px) {
    .nav-links, .nav-actions .btn-outline {
      display: none;
    }
    .hero-title {
      font-size: 2.5rem;
    }
    .filter-grid {
      grid-template-columns: 1fr;
    }
    .services-grid, .providers-grid {
      grid-template-columns: 1fr;
    }
    .footer-columns {
      grid-template-columns: 1fr;
    }
    .vendor-checklist {
      grid-template-columns: 1fr;
    }
    .vendor-section {
      padding: 2.5rem 1.75rem;
    }
    .container, .container-wide {
      width: 100%;
      padding: 0 1rem;
    }
  }
`;

export default function App() {
  const [selectedState, setSelectedState] = useState('Karnataka');
  const [selectedCity, setSelectedCity] = useState('Bengaluru');
  const [selectedService, setSelectedService] = useState('Borewell Drilling');
  const [searchNotification, setSearchNotification] = useState('');

  // Interactive Subterranean Simulator State
  const [depth, setDepth] = useState(480);
  const [casingType, setCasingType] = useState('PVC');
  const [diameter, setDiameter] = useState('6.5');
  const [purpose, setPurpose] = useState('Agriculture / Farm');

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalTitle, setModalTitle] = useState('');
  const [modalSubmitted, setModalSubmitted] = useState(false);
  const [leadForm, setLeadForm] = useState({ name: '', phone: '', city: '' });

  // FAQ Accordion State
  const [openFaq, setOpenFaq] = useState(0);

  const calculation = useMemo(() => {
    const ratePerFoot = diameter === '6.5' ? 95 : 75;
    const casingRate = casingType === 'GI' ? 440 : casingType === 'MS' ? 360 : 250;
    
    // Average 15-20% depth requires outer protective casing pipe
    const casingRequiredFeet = Math.min(100, Math.max(40, Math.floor(depth * 0.18)));
    const drillingAmount = depth * ratePerFoot;
    const casingAmount = casingRequiredFeet * casingRate;
    const compressorCharge = 7500;
    
    const baseSum = drillingAmount + casingAmount + compressorCharge;
    const factor = purpose === 'Industrial' ? 1.15 : 1.0;
    
    const totalEst = Math.round(baseSum * factor);
    const minEst = Math.round((totalEst * 0.92) / 500) * 500;
    const maxEst = Math.round((totalEst * 1.08) / 500) * 500;

    // Calculate percentage for drill-rod visual animation (100 to 1200 ft mapped to 10% - 92% of rock column)
    const drillProgressPercent = Math.min(94, Math.max(12, Math.round(((depth - 100) / 1100) * 82) + 12));

    return {
      drillingAmount,
      casingAmount,
      compressorCharge,
      casingRequiredFeet,
      minEst,
      maxEst,
      drillProgressPercent
    };
  }, [depth, casingType, diameter, purpose]);

  const servicesList = [
    {
      id: 1,
      title: 'Precision Sensor Rig Drilling',
      desc: 'High-torque hydraulic drilling machines designed for hard granite, basalt, and loose soil. Certified geological survey guidance.',
      price: '₹75 / ft',
      tag: 'Most Popular',
      image: 'https://images.unsplash.com/photo-1541888946425-d0fbb186c5f9?auto=format&fit=crop&w=800&q=80'
    },
    {
      id: 2,
      title: 'High-Pressure Air Flushing',
      desc: 'Heavy-duty 1100 CFM air compressor cleaning to clear silt, red mud, and debris, restoring pure crystal water yield.',
      price: '₹4,999',
      tag: 'Fast 2-Hr Service',
      image: 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80'
    },
    {
      id: 3,
      title: 'Submersible Pumps & Installation',
      desc: 'Branded copper submersible pump sets (Texmo, Kirloskar, CRI) with digital control panels, dry-run protectors, and heavy cabling.',
      price: '₹1,499 Setup',
      tag: '100% Genuine',
      image: 'https://images.unsplash.com/photo-1581092335397-9583fe92d232?auto=format&fit=crop&w=800&q=80'
    },
    {
      id: 4,
      title: 'Underwater HD Camera Scanning',
      desc: '360° rotational borehole inspection cameras to locate water fractures, damaged casing, and stuck pump retrieval points.',
      price: '₹3,500',
      tag: 'Advanced Tech',
      image: 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80'
    },
    {
      id: 5,
      title: 'Agricultural Farm Irrigation',
      desc: 'Drip lines, automated manifold valves, rain gun sprinklers, and artificial ground aquifer recharge pits for high farm yields.',
      price: 'Custom Estimate',
      tag: 'Govt Subsidy Support',
      image: 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80'
    },
    {
      id: 6,
      title: 'Emergency Stuck Pump Retrieval',
      desc: 'Heavy winch tackle and robotic pipe grapplers to pull out snapped ropes, jammed pumps, and fallen motors without damaging borewells.',
      price: 'On Inspection',
      tag: '24x7 SOS',
      image: 'https://images.unsplash.com/photo-1581092580497-e0d23cbdf1dc?auto=format&fit=crop&w=800&q=80'
    }
  ];

  const verifiedContractors = [
    {
      id: 1,
      name: 'Sri Venkateshwara Heavy Rigs',
      city: 'Bengaluru & Kolar, KA',
      rating: 4.9,
      reviews: 184,
      specialty: 'High-power 1200+ ft sensor rigs & quick casing installation',
      phone: '+918431738810'
    },
    {
      id: 2,
      name: 'Annapurna Borewell & Pump Care',
      city: 'Hyderabad & Secunderabad, TS',
      rating: 4.85,
      reviews: 129,
      specialty: 'Authorized Texmo / CRI motor service & rapid rewinding',
      phone: '+918431738810'
    },
    {
      id: 3,
      name: 'Kisan Jyoti Irrigation & Flushing',
      city: 'Pune & Ahmednagar, MH',
      rating: 4.92,
      reviews: 147,
      specialty: 'Agricultural deep cleaning, re-drilling and aquifer rejuvenation',
      phone: '+918431738810'
    }
  ];

  const faqs = [
    {
      q: "How does BorewellMart determine drilling charges?",
      a: "Charges are directly determined by feet drilled, standard diameter (4.5 vs 6.5 inch), and casing pipe material (PVC or GI). We eliminate middleman surcharges, giving you direct driller rates."
    },
    {
      q: "What does the GoogleBore ₹999 Vendor Package include?",
      a: "Rig operators and technicians receive an audited 6-month verified listing, Google Business Profile assistance, customer leads routed to their mobile, and zero commission on bookings."
    },
    {
      q: "How do I know what depth to drill on my agricultural farm?",
      a: "Our listed operators work with geological water diviners and groundwater resistivity meter teams to identify fracture seams prior to drilling."
    },
    {
      q: "Can I book emergency pump breakdown services on Sundays?",
      a: "Yes! Our 24x7 emergency callout helpline connects you with duty mechanics equipped with spare capacitors, control panels, and winch gear."
    }
  ];

  const handleSearch = () => {
    setSearchNotification(`Found 14+ verified rigs and pump engineers in ${selectedCity}, ${selectedState} ready for immediate dispatch!`);
  };

  const handleOpenModal = (title: string) => {
    setModalTitle(title);
    setModalSubmitted(false);
    setIsModalOpen(true);
  };

  const handleLeadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!leadForm.name || !leadForm.phone) return;
    setModalSubmitted(true);
    setTimeout(() => {
      setIsModalOpen(false);
      setLeadForm({ name: '', phone: '', city: '' });
    }, 2500);
  };

  return (
    <>
      <style>{cssStyles}</style>

      {/* Top Banner (Full Bleed across viewport) */}
      <div className="top-banner">
        <div className="container-wide">
          <div className="top-banner-inner">
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
              <span className="beacon-pill">
                <span className="pulse-dot"></span>
                LIVE DISPATCH
              </span>
              <span>24/7 Borewell Drilling & Pump Emergency Helpline:</span>
              <a href="tel:+918431738810" style={{ fontWeight: 800, color: '#38bdf8', textDecoration: 'underline' }}>
                +91 84317 38810
              </a>
            </div>
            <div>
              <span style={{ opacity: 0.9 }}>Covering 500+ Taluks & Major Districts across India</span>
            </div>
          </div>
        </div>
      </div>

      {/* Wide Navbar */}
      <header className="navbar-wrapper">
        <div className="container-wide">
          <nav className="navbar">
            <div className="logo-block" onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
              <div className="logo-icon-box">
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                  <path d="M12 2v20M7 7l5-5 5 5M5 21h14"/>
                </svg>
              </div>
              <div className="brand-text">
                <h1>Borewell<span>Mart</span></h1>
                <div className="brand-sub">by GoogleBore.com</div>
              </div>
            </div>

            <ul className="nav-links">
              <li><a href="#services" className="nav-link">Services</a></li>
              <li><a href="#simulator" className="nav-link">Depth & Cost Simulator</a></li>
              <li><a href="#vendor-growth" className="nav-link">Vendor Growth</a></li>
              <li><a href="#contractors" className="nav-link">Verified Rigs</a></li>
              <li><a href="#faq" className="nav-link">FAQ</a></li>
            </ul>

            <div className="nav-actions">
              <button 
                onClick={() => handleOpenModal("Vendor Partner Registration - ₹999 Growth Package")}
                className="btn btn-outline"
              >
                Join as Contractor
              </button>
              <button 
                onClick={() => handleOpenModal("Instant Rig / Service Booking")}
                className="btn btn-primary btn-glow"
              >
                Book a Service
              </button>
            </div>
          </nav>
        </div>
      </header>

      {/* Expansive Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-grid">
            <div>
              <div className="badge-tag-hero">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2L1 21h22L12 2zm0 3.84L19.38 19H4.62L12 5.84zM11 10h2v4h-2zm0 6h2v2h-2z"/>
                </svg>
                India's Certified Borewell & Agricultural Network
              </div>

              <h2 className="hero-title">
                Reliable Groundwater <br />
                <span className="text-gradient">Drilling & Irrigation</span> Experts
              </h2>

              <p className="hero-desc">
                Connect directly with audited sensor hydraulic rigs, heavy air compressor desilting crews, and certified submersible pump mechanics. Transparent per-foot pricing with zero middleman surcharges.
              </p>

              {/* Wide Search & Location Selector */}
              <div className="hero-search-box">
                <div className="filter-grid">
                  <div className="field-group">
                    <label className="field-label">Select State</label>
                    <select 
                      className="field-input" 
                      value={selectedState} 
                      onChange={(e) => setSelectedState(e.target.value)}
                    >
                      <option value="Karnataka">Karnataka</option>
                      <option value="Telangana">Telangana</option>
                      <option value="Maharashtra">Maharashtra</option>
                      <option value="Tamil Nadu">Tamil Nadu</option>
                      <option value="Andhra Pradesh">Andhra Pradesh</option>
                      <option value="Chhattisgarh">Chhattisgarh</option>
                    </select>
                  </div>

                  <div className="field-group">
                    <label className="field-label">City / District</label>
                    <select 
                      className="field-input" 
                      value={selectedCity} 
                      onChange={(e) => setSelectedCity(e.target.value)}
                    >
                      <option value="Bengaluru">Bengaluru</option>
                      <option value="Hyderabad">Hyderabad</option>
                      <option value="Pune">Pune</option>
                      <option value="Kolar">Kolar</option>
                      <option value="Mysuru">Mysuru</option>
                      <option value="Bilaspur">Bilaspur</option>
                    </select>
                  </div>

                  <div className="field-group">
                    <label className="field-label">Requirement</label>
                    <select 
                      className="field-input" 
                      value={selectedService} 
                      onChange={(e) => setSelectedService(e.target.value)}
                    >
                      <option value="Borewell Drilling">New Borewell Drilling</option>
                      <option value="Air Compressor Flushing">Compressor Flushing & Cleaning</option>
                      <option value="Submersible Motor Setup">Submersible Pump Installation</option>
                      <option value="HD Camera Scanning">HD Bore Camera Scanning</option>
                    </select>
                  </div>

                  <button 
                    onClick={handleSearch}
                    className="btn btn-primary" 
                    style={{ height: '48px', whiteSpace: 'nowrap', padding: '0 1.85rem' }}
                  >
                    Find Drillers
                  </button>
                </div>

                {searchNotification && (
                  <div style={{ marginTop: '1.25rem', padding: '0.85rem 1.25rem', background: '#e0f2fe', borderRadius: '8px', color: '#0369a1', fontSize: '0.92rem', fontWeight: 700 }}>
                    {searchNotification}
                  </div>
                )}
              </div>
            </div>

            {/* Visual Montage with Animated Floating Badges */}
            <div className="hero-visual-wrapper">
              <div className="hero-image-card">
                <img 
                  src="https://images.unsplash.com/photo-1541888946425-d0fbb186c5f9?auto=format&fit=crop&w=1000&q=80" 
                  alt="Industrial Borewell Rig" 
                />
              </div>

              {/* Floating Badge 1 */}
              <div className="floating-badge badge-one">
                <div className="badge-icon-box" style={{ background: '#10b981' }}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <path d="M20 6L9 17l-5-5"/>
                  </svg>
                </div>
                <div>
                  <div className="badge-title">99.4% Success</div>
                  <div className="badge-subtitle">Groundwater Strike Rate</div>
                </div>
              </div>

              {/* Floating Badge 2 */}
              <div className="floating-badge badge-two">
                <div className="badge-icon-box" style={{ background: '#0284c7' }}>
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M12 2v20M7 7l5-5 5 5M5 21h14"/>
                  </svg>
                </div>
                <div>
                  <div className="badge-title">5,200+ Drillers</div>
                  <div className="badge-subtitle">Verified Rig Fleets</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Full-Bleed Continuous Ticker */}
      <div className="ticker-wrap">
        <div className="ticker-title">Authorized Equipment Brands & Technology Partners</div>
        <div className="ticker-marquee">
          {['KIRLOSKAR BROTHERS', 'C.R.I. PUMPS', 'TEXMO AQUA', 'FINOLEX PIPES', 'FALCON SUBMERSIBLES', 'ASHIRVAD PIPES', 'KSB PUMPS', 'L&T CONTROLLERS'].map((brand, idx) => (
            <div key={idx} className="brand-logo-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="#0284c7">
                <circle cx="12" cy="12" r="8"/>
              </svg>
              {brand}
            </div>
          ))}
          {['KIRLOSKAR BROTHERS', 'C.R.I. PUMPS', 'TEXMO AQUA', 'FINOLEX PIPES', 'FALCON SUBMERSIBLES', 'ASHIRVAD PIPES', 'KSB PUMPS', 'L&T CONTROLLERS'].map((brand, idx) => (
            <div key={`repeat-${idx}`} className="brand-logo-item">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="#0284c7">
                <circle cx="12" cy="12" r="8"/>
              </svg>
              {brand}
            </div>
          ))}
        </div>
      </div>

      {/* Wide Interactive Subterranean Simulator */}
      <section className="section" id="simulator">
        <div className="container">
          <div className="section-head">
            <span className="pill-badge">Live Subterranean Simulation</span>
            <h2 className="section-title">Visual Depth Simulator & Cost Estimator</h2>
            <p className="section-desc">
              Drag the depth slider to inspect simulated earth strata layers, watch the animated rig drill head penetrate through hard granite into the deep aquifer, and calculate indicative rates.
            </p>
          </div>

          <div className="estimator-card">
            <div className="estimator-grid">
              
              {/* Geological Cross Section Visualization Column */}
              <div className="subsurface-visualizer">
                <div className="subsurface-title">
                  <span>Geological Strata</span>
                  <span style={{ color: '#f59e0b', fontFamily: 'JetBrains Mono', fontWeight: 800 }}>{depth} FT DRILL</span>
                </div>

                <div className="rock-column">
                  {/* Topsoil Layer */}
                  <div className="layer-topsoil">
                    <span>0 - 100 FT (Topsoil / Red Silt Layer)</span>
                  </div>

                  {/* Weathered Granitic Layer */}
                  <div className="layer-weathered">
                    <span>100 - 350 FT (Weathered Fissured Rock)</span>
                  </div>

                  {/* Hard Bedrock & Aquifer */}
                  <div className="layer-bedrock">
                    <span>350+ FT (Hard Granite Fractures)</span>
                    <div className="water-strike-zone">
                      <span>💦 WATER BEARING AQUIFER ZONE</span>
                    </div>
                  </div>

                  {/* Animated Drill Rod extending downwards based on slider */}
                  <div 
                    className="drill-rod" 
                    style={{ height: `${calculation.drillProgressPercent}%` }}
                  >
                    <div className="drill-bit"></div>
                  </div>
                </div>

                <div style={{ marginTop: '1.25rem', fontSize: '0.85rem', color: '#94a3b8', textAlign: 'center' }}>
                  Drill Bit Active • Hard Rock RPM 850
                </div>
              </div>

              {/* Parameter Controls */}
              <div className="estimator-inputs">
                <div className="range-header">
                  <span style={{ fontWeight: 800, fontSize: '1.15rem' }}>Bore Depth Target:</span>
                  <span className="depth-badge">{depth} Feet</span>
                </div>

                <input 
                  type="range" 
                  min="100" 
                  max="1200" 
                  step="25" 
                  value={depth} 
                  onChange={(e) => setDepth(Number(e.target.value))}
                  className="range-slider"
                />

                <div style={{ marginBottom: '1.65rem' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '0.65rem' }}>
                    Rig Drilling Diameter (Inches)
                  </div>
                  <div className="pill-options">
                    {['4.5', '6.5'].map((d) => (
                      <button 
                        key={d} 
                        type="button"
                        onClick={() => setDiameter(d)}
                        className={`pill-option ${diameter === d ? 'active' : ''}`}
                      >
                        {d}" Heavy Standard
                      </button>
                    ))}
                  </div>
                </div>

                <div style={{ marginBottom: '1.65rem' }}>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '0.65rem' }}>
                    Casing Pipe Material (Soil Protection)
                  </div>
                  <div className="pill-options">
                    {[
                      { id: 'PVC', name: 'Standard Heavy PVC' },
                      { id: 'MS', name: 'Mild Steel (MS Casing)' },
                      { id: 'GI', name: 'Galvanized Iron (GI)' }
                    ].map((m) => (
                      <button 
                        key={m.id} 
                        type="button"
                        onClick={() => setCasingType(m.id)}
                        className={`pill-option ${casingType === m.id ? 'active' : ''}`}
                      >
                        {m.name}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#64748b', textTransform: 'uppercase', marginBottom: '0.65rem' }}>
                    Property Application
                  </div>
                  <div className="pill-options">
                    {['Agriculture / Farm', 'Residential Villa', 'Industrial / Commercial'].map((p) => (
                      <button 
                        key={p} 
                        type="button"
                        onClick={() => setPurpose(p)}
                        className={`pill-option ${purpose === p ? 'active' : ''}`}
                      >
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Price Calculation Output */}
              <div className="estimator-summary">
                <div>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#0f172a', marginBottom: '1.25rem' }}>
                    Estimated Expense Breakdown
                  </h3>

                  <div className="price-calc-box">
                    <div className="calc-line">
                      <span>Bore Rig Boring ({depth} ft):</span>
                      <strong>₹{calculation.drillingAmount.toLocaleString()}</strong>
                    </div>
                    <div className="calc-line">
                      <span>Casing Pipe (~{calculation.casingRequiredFeet} ft {casingType}):</span>
                      <strong>₹{calculation.casingAmount.toLocaleString()}</strong>
                    </div>
                    <div className="calc-line">
                      <span>Air Compressor Flushing:</span>
                      <strong>₹{calculation.compressorCharge.toLocaleString()}</strong>
                    </div>
                    <div className="calc-total">
                      <span style={{ fontWeight: 700, color: '#0f172a' }}>Expected Range:</span>
                      <span className="calc-price">
                        ₹{(calculation.minEst / 1000).toFixed(1)}k - ₹{(calculation.maxEst / 1000).toFixed(1)}k
                      </span>
                    </div>
                  </div>

                  <p style={{ fontSize: '0.85rem', color: '#64748b', lineHeight: 1.55 }}>
                    *Indicative calculation. Final depth and casing pipe consumption depend on immediate rock hardness at your site.
                  </p>
                </div>

                <button 
                  onClick={() => handleOpenModal(`Formal Quotation: ${depth}ft ${purpose} Borewell`)}
                  className="btn btn-accent btn-glow" 
                  style={{ width: '100%', padding: '1rem', marginTop: '1.5rem', fontSize: '1rem' }}
                >
                  Request Official Quotation
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Expansive Core Services */}
      <section className="section section-alt" id="services">
        <div className="container">
          <div className="section-head">
            <span className="pill-badge">Full Turnkey Solutions</span>
            <h2 className="section-title">Comprehensive Borewell & Water Services</h2>
            <p className="section-desc">
              From initial hydro-geological surveys to precision sensor boring, high-pressure desilting, and submersible pump installation.
            </p>
          </div>

          <div className="services-grid">
            {servicesList.map((svc) => (
              <div key={svc.id} className="service-card">
                <div className="service-thumb">
                  <img src={svc.image} alt={svc.title} />
                  <span className="service-tag">{svc.tag}</span>
                </div>
                <div className="service-body">
                  <div>
                    <h3 className="service-title">{svc.title}</h3>
                    <p className="service-desc">{svc.desc}</p>
                  </div>
                  <div className="service-bottom">
                    <div className="service-cost-tag">
                      From: <span>{svc.price}</span>
                    </div>
                    <button 
                      onClick={() => handleOpenModal(`Book Service: ${svc.title}`)}
                      className="btn btn-outline" 
                      style={{ padding: '0.55rem 1.25rem', fontSize: '0.88rem' }}
                    >
                      Book Now
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Wide Vendor Growth Package Banner */}
      <section className="section" id="vendor-growth">
        <div className="container">
          <div className="vendor-section">
            <div className="vendor-grid">
              <div>
                <span className="offer-badge">Contractor Growth Initiative</span>
                <h2 className="vendor-title">
                  Grow Your Borewell & Pump Business Across Your District
                </h2>
                <p style={{ opacity: 0.9, fontSize: '1.15rem', lineHeight: 1.7 }}>
                  Join India’s premier verified borewell marketplace. Receive verified farmer and residential homeowner calls straight to your mobile.
                </p>

                <ul className="vendor-checklist">
                  <li className="vendor-check-item">
                    <svg width="22" height="22" fill="none" stroke="#38bdf8" strokeWidth="3" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>
                    Google Business Profile Optimization
                  </li>
                  <li className="vendor-check-item">
                    <svg width="22" height="22" fill="none" stroke="#38bdf8" strokeWidth="3" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>
                    Direct High-Intent Customer Phone Leads
                  </li>
                  <li className="vendor-check-item">
                    <svg width="22" height="22" fill="none" stroke="#38bdf8" strokeWidth="3" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>
                    Dedicated District Portfolio Page
                  </li>
                  <li className="vendor-check-item">
                    <svg width="22" height="22" fill="none" stroke="#38bdf8" strokeWidth="3" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>
                    Zero Commission on Completed Jobs
                  </li>
                </ul>
              </div>

              <div className="pricing-glass-card">
                <span className="strikethrough-tag">Regular Value ₹10,000+</span>
                <div className="deal-price">₹999</div>
                <div style={{ fontSize: '1.05rem', fontWeight: 600, opacity: 0.95, marginBottom: '2rem' }}>
                  Full 6-Month Listing & Digital Presence Package
                </div>
                <button 
                  onClick={() => handleOpenModal("Vendor Partner Registration - ₹999 Growth Package")}
                  className="btn btn-accent btn-glow" 
                  style={{ width: '100%', padding: '1.05rem', fontSize: '1.1rem' }}
                >
                  Claim Vendor Package Now
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Expansive Regional Contractors */}
      <section className="section section-alt" id="contractors">
        <div className="container">
          <div className="section-head">
            <span className="pill-badge">Field Audited Operators</span>
            <h2 className="section-title">Top Rated Drillers & Mechanics</h2>
            <p className="section-desc">
              All contractors undergo rig machinery checks, insurance verification, and transparent per-foot pricing audits.
            </p>
          </div>

          <div className="providers-grid">
            {verifiedContractors.map((c) => (
              <div key={c.id} className="provider-card">
                <div className="provider-header">
                  <div>
                    <h3 className="provider-name">{c.name}</h3>
                    <div className="provider-city">
                      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
                        <circle cx="12" cy="10" r="3"/>
                      </svg>
                      {c.city}
                    </div>
                  </div>
                  <span className="badge-verified-pro">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                    Verified Pro
                  </span>
                </div>

                <div className="provider-rating-row">
                  <span className="stars">★ {c.rating}</span>
                  <span className="review-count">({c.reviews} Verified Customer Reviews)</span>
                </div>

                <p style={{ fontSize: '0.94rem', color: '#475569', minHeight: '48px', marginBottom: '1.5rem', lineHeight: 1.55 }}>
                  {c.specialty}
                </p>

                <div style={{ display: 'flex', gap: '0.85rem' }}>
                  <a 
                    href={`tel:${c.phone}`} 
                    className="btn btn-primary" 
                    style={{ flex: 1, padding: '0.7rem', fontSize: '0.9rem' }}
                  >
                    Direct Call
                  </a>
                  <button 
                    onClick={() => handleOpenModal(`Request Quote from ${c.name}`)}
                    className="btn btn-outline" 
                    style={{ flex: 1, padding: '0.7rem', fontSize: '0.9rem' }}
                  >
                    Get Quote
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Expansive FAQ */}
      <section className="section" id="faq">
        <div className="container">
          <div className="section-head">
            <span className="pill-badge">Common Queries</span>
            <h2 className="section-title">Frequently Asked Questions</h2>
            <p className="section-desc">
              Clear answers regarding water divining, casing pipes, and emergency callout support.
            </p>
          </div>

          <div className="faq-wrapper">
            {faqs.map((f, i) => (
              <div key={i} className="faq-accordion-item">
                <button 
                  className="faq-btn" 
                  onClick={() => setOpenFaq(openFaq === i ? -1 : i)}
                >
                  <span>{f.q}</span>
                  <span style={{ fontSize: '1.5rem', color: '#0284c7', fontWeight: 800 }}>
                    {openFaq === i ? '−' : '+'}
                  </span>
                </button>
                {openFaq === i && (
                  <div className="faq-text">{f.a}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Wide Footer */}
      <footer className="site-footer">
        <div className="container">
          <div className="footer-columns">
            <div>
              <div className="logo-block" style={{ marginBottom: '1.5rem' }}>
                <div className="logo-icon-box">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                    <path d="M12 2v20M7 7l5-5 5 5M5 21h14"/>
                  </svg>
                </div>
                <div className="brand-text">
                  <h3 style={{ color: '#ffffff', fontSize: '1.45rem', fontWeight: 800 }}>
                    Borewell<span style={{ color: '#38bdf8' }}>Mart</span>
                  </h3>
                  <div className="brand-sub" style={{ color: '#94a3b8' }}>by GoogleBore.com</div>
                </div>
              </div>
              <p style={{ fontSize: '0.96rem', lineHeight: 1.65, marginBottom: '1.5rem', maxWidth: '440px' }}>
                India's foremost digital network connecting agricultural cultivators, residential property owners, and industrial units with certified drilling machinery.
              </p>
              <div style={{ color: '#ffffff', fontSize: '0.98rem' }}>
                Helpline: <strong style={{ color: '#38bdf8' }}>+91 84317 38810</strong>
              </div>
            </div>

            <div>
              <h4 className="footer-heading">Services</h4>
              <ul className="footer-links">
                <li><a href="#services">Precision Rig Drilling</a></li>
                <li><a href="#services">Air Flushing & Desilting</a></li>
                <li><a href="#services">Submersible Pump Repair</a></li>
                <li><a href="#services">Underwater HD Camera</a></li>
                <li><a href="#services">Farm Drip & Sprinklers</a></li>
              </ul>
            </div>

            <div>
              <h4 className="footer-heading">Major Hubs</h4>
              <ul className="footer-links">
                <li><a href="#contractors">Bengaluru, Karnataka</a></li>
                <li><a href="#contractors">Hyderabad, Telangana</a></li>
                <li><a href="#contractors">Pune, Maharashtra</a></li>
                <li><a href="#contractors">Kolar Gold Fields</a></li>
                <li><a href="#contractors">Bilaspur & Raipur</a></li>
              </ul>
            </div>

            <div>
              <h4 className="footer-heading">Rig Operator Listing</h4>
              <p style={{ fontSize: '0.92rem', marginBottom: '1.25rem', lineHeight: 1.55 }}>
                Own a rig or motor rewinding shop? Get qualified leads with our 6-month growth plan.
              </p>
              <button 
                onClick={() => handleOpenModal("Vendor Partner Registration - ₹999 Growth Package")}
                className="btn btn-accent" 
                style={{ width: '100%', fontSize: '0.95rem' }}
              >
                Register Business (₹999)
              </button>
            </div>
          </div>

          <div className="footer-bottom-bar">
            <div>© {new Date().getFullYear()} GoogleBore / BorewellMart. All rights reserved.</div>
            <div style={{ display: 'flex', gap: '2rem' }}>
              <a href="#simulator">Cost Calculator</a>
              <a href="#vendor-growth">Contractor Package</a>
              <a href="#faq">Privacy Policy</a>
              <a href="#faq">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>

      {/* WhatsApp Quick Action */}
      <div className="floating-quick-action">
        <a 
          href="https://wa.me/918431738810?text=Hello%20BorewellMart,%20I%20need%20borewell%20service" 
          target="_blank" 
          rel="noopener noreferrer"
          className="whatsapp-pulse-btn"
          aria-label="WhatsApp Support"
        >
          <svg width="34" height="34" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12.04 2c-5.46 0-9.91 4.45-9.91 9.91 0 1.75.46 3.45 1.32 4.95L2.05 22l5.25-1.38c1.45.79 3.08 1.21 4.74 1.21 5.46 0 9.91-4.45 9.91-9.91 0-2.65-1.03-5.14-2.9-7.01A9.816 9.816 0 0 0 12.04 2m.01 1.67c2.2 0 4.26.86 5.82 2.42a8.225 8.225 0 0 1 2.41 5.83c0 4.54-3.7 8.24-8.24 8.24-1.48 0-2.93-.4-4.2-1.15l-.3-.18-3.12.82.83-3.04-.2-.31a8.19 8.19 0 0 1-1.26-4.38c0-4.54 3.7-8.24 8.24-8.24m4.52 11.66c-.25-.13-1.47-.72-1.7-.81-.23-.08-.39-.13-.56.13-.17.25-.64.81-.79.97-.14.17-.29.19-.54.06-.25-.13-1.06-.39-2.02-1.25-.75-.67-1.26-1.5-1.4-1.75-.15-.25-.02-.39.11-.51.11-.11.25-.29.37-.43.13-.15.17-.25.25-.42.08-.17.04-.31-.02-.44-.06-.13-.56-1.35-.77-1.85-.2-.49-.41-.42-.56-.43h-.48c-.17 0-.44.06-.67.31-.23.25-.88.86-.88 2.1 0 1.24.9 2.44 1.03 2.61.13.17 1.77 2.7 4.29 3.79.6.26 1.07.41 1.44.53.6.19 1.15.16 1.58.1.48-.07 1.47-.6 1.68-1.18.21-.58.21-1.07.15-1.18-.07-.12-.23-.19-.48-.31z"/>
          </svg>
        </a>
      </div>

      {/* Modal Dialog */}
      {isModalOpen && (
        <div className="modal-backdrop" onClick={() => setIsModalOpen(false)}>
          <div className="modal-container" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close-btn" onClick={() => setIsModalOpen(false)}>✕</button>

            {modalSubmitted ? (
              <div style={{ textAlign: 'center', padding: '1.75rem 0' }}>
                <div style={{
                  width: '68px',
                  height: '68px',
                  borderRadius: '50%',
                  background: '#dcfce7',
                  color: '#15803d',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 1.5rem'
                }}>
                  <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <polyline points="20 6 9 17 4 12"/>
                  </svg>
                </div>
                <h3 style={{ fontSize: '1.45rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.65rem' }}>
                  Request Confirmed!
                </h3>
                <p style={{ color: '#64748b', fontSize: '1rem', lineHeight: 1.6 }}>
                  Our verified district coordinator will call you at <strong>{leadForm.phone}</strong> within 15 minutes with complete quotation details.
                </p>
              </div>
            ) : (
              <div>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', marginBottom: '0.65rem' }}>
                  {modalTitle}
                </h3>
                <p style={{ color: '#64748b', fontSize: '0.92rem', marginBottom: '1.75rem', lineHeight: 1.5 }}>
                  Enter your details below to connect directly with the nearest active rig operator.
                </p>

                <form onSubmit={handleLeadSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
                  <div className="field-group">
                    <label className="field-label">Full Name</label>
                    <input 
                      type="text" 
                      required 
                      className="field-input" 
                      placeholder="e.g. Ramesh Gowda"
                      value={leadForm.name}
                      onChange={(e) => setLeadForm({ ...leadForm, name: e.target.value })}
                    />
                  </div>

                  <div className="field-group">
                    <label className="field-label">Mobile Number (WhatsApp)</label>
                    <input 
                      type="tel" 
                      required 
                      className="field-input" 
                      placeholder="e.g. 9876543210"
                      value={leadForm.phone}
                      onChange={(e) => setLeadForm({ ...leadForm, phone: e.target.value })}
                    />
                  </div>

                  <div className="field-group">
                    <label className="field-label">City / Village Location</label>
                    <input 
                      type="text" 
                      className="field-input" 
                      placeholder="e.g. Devanahalli, Bengaluru Rural"
                      value={leadForm.city}
                      onChange={(e) => setLeadForm({ ...leadForm, city: e.target.value })}
                    />
                  </div>

                  <button 
                    type="submit" 
                    className="btn btn-primary btn-glow" 
                    style={{ marginTop: '0.75rem', padding: '0.95rem', fontSize: '1rem' }}
                  >
                    Submit Booking Request
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
