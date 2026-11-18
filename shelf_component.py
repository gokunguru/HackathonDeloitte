"""Interactive 3D VHS-style Bid Project Shelf component for Deloitte Secure Bid Squad."""

import json
from typing import Any, Dict

import config


def _safe_json(data: Any) -> str:
    """Serialize data to JSON safe for embedding inside HTML <script> tags."""
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render_shelf_html(shelf_payload: Dict[str, Any]) -> str:
    """Render the self-contained 3D Bid Project Shelf HTML/CSS/JS component."""
    theme = config.SUPABASE_THEME
    payload_json = _safe_json(shelf_payload)
    theme_json = _safe_json(theme)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{config.APP_TITLE}</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
  :root {{
    --bg: {theme["bg"]};
    --surface: {theme["surface"]};
    --card: {theme["card"]};
    --border: {theme["border"]};
    --border-input: {theme["border_input"]};
    --accent: {theme["accent"]};
    --mint: {theme["mint"]};
    --text: {theme["text"]};
    --muted: {theme["muted"]};
    --smoke: {theme["smoke"]};
    --danger: {theme["danger"]};
    --warning: {theme["warning"]};
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  html, body {{
    width: 100%;
    height: 100%;
    background: var(--bg);
    color: var(--text);
    font-family: var(--font-sans);
    overflow: hidden;
    user-select: none;
    -webkit-font-smoothing: antialiased;
  }}

  .stage {{
    position: relative;
    width: 100%;
    height: 100vh;
    background:
      linear-gradient(to right, rgba(46, 46, 46, 0.16) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(46, 46, 46, 0.16) 1px, transparent 1px),
      var(--bg);
    background-size: 48px 48px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
    cursor: none;
  }}

  /* Top HUD Bar */
  .hud-bar {{
    position: relative;
    z-index: 30;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 10px 18px;
    background: rgba(24, 24, 24, 0.94);
    border-bottom: 1px solid var(--border);
    backdrop-filter: blur(8px);
    cursor: default;
  }}

  .hud-brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-family: var(--font-mono);
    font-size: 12px;
    letter-spacing: 0.08em;
    color: var(--text);
    font-weight: 600;
  }}

  .hud-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    box-shadow: 0 0 8px var(--accent);
  }}

  .hud-metrics {{
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }}

  .hud-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 9px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 4px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--muted);
  }}

  .hud-pill strong {{ color: var(--text); font-weight: 600; }}
  .hud-pill.accent {{
    border-color: rgba(62, 207, 142, 0.4);
    background: rgba(62, 207, 142, 0.08);
  }}
  .hud-pill.accent strong {{ color: var(--accent); }}
  .hud-pill.danger {{
    border-color: rgba(239, 68, 68, 0.45);
    background: rgba(239, 68, 68, 0.08);
  }}
  .hud-pill.danger strong {{ color: var(--danger); }}

  /* 3D Shelf Viewport */
  .shelf-viewport {{
    position: relative;
    flex: 1;
    width: 100%;
    perspective: 1450px;
    perspective-origin: 50% 48%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }}

  .shelf-floor {{
    position: absolute;
    bottom: 58px;
    left: 6%;
    right: 6%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--border-input) 15%, var(--accent) 50%, var(--border-input) 85%, transparent);
    opacity: 0.55;
    pointer-events: none;
  }}

  .shelf-track {{
    position: relative;
    width: 100%;
    height: 370px;
    transform-style: preserve-3d;
    pointer-events: none;
  }}

  .dossier-slot {{
    position: absolute;
    left: 50%;
    top: 50%;
    width: 70px;
    height: 320px;
    margin-left: -35px;
    margin-top: -160px;
    transform-style: preserve-3d;
    pointer-events: auto;
    will-change: transform;
  }}

  .dossier-box {{
    position: relative;
    width: 100%;
    height: 100%;
    transform-style: preserve-3d;
    will-change: transform;
  }}

  /* Spine Face */
  .face-spine {{
    position: absolute;
    inset: 0;
    width: 70px;
    height: 320px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 3px;
    transform: translateZ(108px);
    backface-visibility: hidden;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    padding: 12px 6px;
    transition: border-color 0.2s ease, background 0.2s ease;
  }}

  .dossier-slot:hover .face-spine {{
    border-color: var(--accent);
    background: var(--surface);
  }}
  .dossier-slot.is-locked .face-spine {{
    border-color: rgba(239, 68, 68, 0.45);
  }}

  .spine-vol {{
    font-family: var(--font-mono);
    font-size: 9px;
    font-weight: 700;
    color: var(--accent);
    letter-spacing: 0.06em;
    text-align: center;
  }}
  .dossier-slot.is-locked .spine-vol {{ color: var(--danger); }}

  .spine-title {{
    writing-mode: vertical-rl;
    transform: rotate(180deg);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: var(--text);
    text-transform: uppercase;
    white-space: nowrap;
    max-height: 196px;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .spine-footer {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 5px;
    width: 100%;
  }}

  .spine-code {{
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--smoke);
  }}

  .spine-bar {{
    width: 36px;
    height: 4px;
    border-radius: 2px;
    background: var(--border-input);
  }}
  .dossier-slot.is-active .spine-bar {{ background: var(--accent); }}
  .dossier-slot.is-locked .spine-bar {{ background: var(--danger); }}

  /* Cover Face */
  .face-cover {{
    position: absolute;
    top: 0;
    left: 70px;
    width: 216px;
    height: 320px;
    background: var(--surface);
    border: 1px solid var(--border-input);
    border-radius: 4px;
    transform-origin: left center;
    transform: translateZ(108px) rotateY(90deg);
    backface-visibility: hidden;
    padding: 15px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }}

  .dossier-slot.is-active .face-cover {{ border-color: var(--accent); }}
  .dossier-slot.is-locked.is-active .face-cover {{ border-color: var(--danger); }}

  .face-left {{
    position: absolute;
    top: 0;
    left: -216px;
    width: 216px;
    height: 320px;
    background: #141414;
    border: 1px solid var(--border);
    transform-origin: right center;
    transform: translateZ(108px) rotateY(-90deg);
    backface-visibility: hidden;
  }}

  .face-top {{
    position: absolute;
    top: -216px;
    left: 0;
    width: 70px;
    height: 216px;
    background: #1b1b1b;
    border: 1px solid var(--border);
    transform-origin: bottom center;
    transform: translateZ(108px) rotateX(90deg);
    backface-visibility: hidden;
  }}

  .face-spine *, .face-cover * {{
    pointer-events: none;
  }}

  .cover-grid-bg {{
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(to right, rgba(62, 207, 142, 0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(62, 207, 142, 0.05) 1px, transparent 1px);
    background-size: 20px 20px;
    pointer-events: none;
  }}
  .dossier-slot.is-locked .cover-grid-bg {{
    background-image:
      linear-gradient(to right, rgba(239, 68, 68, 0.07) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(239, 68, 68, 0.07) 1px, transparent 1px);
  }}

  .cover-top {{ position: relative; z-index: 2; display: flex; flex-direction: column; gap: 5px; }}
  .cover-header-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--smoke);
    letter-spacing: 0.06em;
    border-bottom: 1px solid var(--border);
    padding-bottom: 6px;
  }}
  .cover-tag {{ color: var(--accent); font-weight: 700; }}
  .cover-tag.locked {{ color: var(--danger); }}
  .cover-vol {{
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    color: var(--accent);
    margin-top: 2px;
  }}
  .dossier-slot.is-locked .cover-vol {{ color: var(--danger); }}
  .cover-title {{
    font-size: 15px;
    font-weight: 700;
    line-height: 1.25;
    color: var(--text);
  }}
  .cover-client {{
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--muted);
  }}
  .cover-meta-row {{
    display: flex;
    gap: 6px;
    margin-top: 4px;
    flex-wrap: wrap;
  }}
  .cover-chip {{
    font-family: var(--font-mono);
    font-size: 9px;
    padding: 2px 6px;
    border-radius: 3px;
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--muted);
  }}

  .cover-svg-wrap {{
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 4px 0;
  }}

  .cover-bottom {{
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top: 1px solid var(--border);
    padding-top: 9px;
  }}
  .cover-kpi {{
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
  }}
  .cover-kpi.locked {{ color: var(--danger); }}
  .cover-open-hint {{
    font-family: var(--font-mono);
    font-size: 9px;
    color: var(--text);
    background: rgba(62, 207, 142, 0.14);
    border: 1px solid rgba(62, 207, 142, 0.4);
    padding: 3px 7px;
    border-radius: 3px;
  }}
  .dossier-slot.is-locked .cover-open-hint {{
    background: rgba(239, 68, 68, 0.14);
    border-color: rgba(239, 68, 68, 0.45);
    color: var(--danger);
  }}

  /* Bottom Controls */
  .controls-bar {{
    position: relative;
    z-index: 30;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 18px;
    background: rgba(24, 24, 24, 0.94);
    border-top: 1px solid var(--border);
    cursor: default;
  }}
  .vol-pills {{ display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }}
  .vol-pill {{
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 11px;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.15s ease;
  }}
  .vol-pill:hover {{ border-color: var(--border-input); color: var(--text); }}
  .vol-pill.active {{
    border-color: var(--accent);
    color: var(--accent);
    background: rgba(62, 207, 142, 0.1);
  }}
  .vol-pill.locked {{ border-color: rgba(239, 68, 68, 0.4); color: var(--danger); }}
  .nav-actions {{ display: flex; align-items: center; gap: 8px; }}
  .nav-btn {{
    background: var(--card);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 11px;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
  }}
  .nav-btn:hover {{ border-color: var(--accent); }}
  .nav-btn.primary {{
    background: var(--accent);
    color: #0d1612;
    border-color: var(--accent);
    font-weight: 700;
  }}
  .nav-btn.primary:hover {{ background: var(--mint); }}
  .nav-hint {{
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--smoke);
    margin-right: 6px;
  }}

  /* Custom Ring Cursor */
  .custom-cursor {{
    position: fixed;
    top: 0;
    left: 0;
    width: 28px;
    height: 28px;
    border: 1.5px solid var(--accent);
    border-radius: 50%;
    pointer-events: none;
    z-index: 9999;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: width 0.18s ease, height 0.18s ease, background 0.18s ease, border-color 0.18s ease, opacity 0.15s ease;
    opacity: 0;
  }}
  .custom-cursor-label {{
    font-family: var(--font-mono);
    font-size: 9px;
    font-weight: 700;
    color: #0d1612;
    letter-spacing: 0.06em;
    opacity: 0;
    white-space: nowrap;
  }}
  .custom-cursor.on-spine {{ width: 14px; height: 14px; border-color: var(--text); }}
  .custom-cursor.on-cover {{ width: 84px; height: 84px; background: var(--accent); border-color: var(--accent); }}
  .custom-cursor.on-cover.locked {{ background: var(--danger); border-color: var(--danger); }}
  .custom-cursor.on-cover .custom-cursor-label {{ opacity: 1; }}

  /* Full-Screen War Room Sheet */
  .sheet-overlay {{
    position: fixed;
    inset: 0;
    z-index: 200;
    background: var(--bg);
    display: none;
    flex-direction: column;
    overflow: hidden;
    cursor: default;
  }}
  .sheet-overlay.is-open {{ display: flex; }}

  .sheet-topbar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    padding: 12px 22px;
    background: var(--card);
    border-bottom: 1px solid var(--border);
  }}
  .sheet-title-group {{ display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }}
  .sheet-vol-badge {{
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    color: var(--accent);
    background: rgba(62, 207, 142, 0.1);
    border: 1px solid rgba(62, 207, 142, 0.35);
    padding: 4px 8px;
    border-radius: 4px;
  }}
  .sheet-title {{ font-size: 15px; font-weight: 700; color: var(--text); }}
  .sheet-subtitle {{ font-family: var(--font-mono); font-size: 11px; color: var(--smoke); }}

  .agent-strip {{
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }}
  .agent-pill {{
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--accent);
    background: rgba(62, 207, 142, 0.08);
    border: 1px solid rgba(62, 207, 142, 0.3);
    padding: 3px 7px;
    border-radius: 3px;
  }}

  .sheet-close-btn {{
    background: var(--surface);
    border: 1px solid var(--border-input);
    color: var(--text);
    font-family: var(--font-mono);
    font-size: 11px;
    padding: 6px 12px;
    border-radius: 4px;
    cursor: pointer;
  }}
  .sheet-close-btn:hover {{ border-color: var(--accent); color: var(--accent); }}

  .sheet-body {{
    flex: 1;
    overflow-y: auto;
    padding: 18px 22px 28px;
    max-width: 1360px;
    width: 100%;
    margin: 0 auto;
  }}

  /* Executive Intelligence Strip (3 smart cards) */
  .exec-strip {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 16px;
  }}
  @media (max-width: 980px) {{
    .exec-strip {{ grid-template-columns: 1fr; }}
  }}

  .panel {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px 16px;
  }}
  .panel-title {{
    font-family: var(--font-mono);
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--smoke);
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}

  .dim-row {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-top: 6px;
    font-size: 11px;
    color: var(--muted);
  }}
  .dim-bar-bg {{
    flex: 1;
    height: 5px;
    background: var(--surface);
    border-radius: 3px;
    overflow: hidden;
    max-width: 110px;
  }}
  .dim-bar-fill {{
    height: 100%;
    background: var(--accent);
    border-radius: 3px;
  }}

  /* Prioritized 2-Column War Room */
  .warroom-grid {{
    display: grid;
    grid-template-columns: 64% 1fr;
    gap: 16px;
    align-items: start;
  }}
  @media (max-width: 980px) {{
    .warroom-grid {{ grid-template-columns: 1fr; }}
  }}

  .primary-col, .supporting-col {{
    display: flex;
    flex-direction: column;
    gap: 14px;
  }}

  /* Segmented Switcher */
  .seg-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    flex-wrap: wrap;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px;
  }}
  .seg-tabs {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .seg-btn {{
    background: transparent;
    border: 1px solid transparent;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    padding: 6px 11px;
    border-radius: 4px;
    cursor: pointer;
  }}
  .seg-btn:hover {{ color: var(--text); }}
  .seg-btn.active {{
    background: var(--surface);
    border-color: var(--accent);
    color: var(--accent);
  }}

  .tag-chip {{
    display: inline-block;
    font-family: var(--font-mono);
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 3px;
    border: 1px solid var(--border-input);
    color: var(--muted);
    background: var(--surface);
  }}
  .tag-chip.accent {{ border-color: rgba(62, 207, 142, 0.45); color: var(--accent); background: rgba(62, 207, 142, 0.08); }}
  .tag-chip.danger {{ border-color: rgba(239, 68, 68, 0.45); color: var(--danger); background: rgba(239, 68, 68, 0.08); }}
  .tag-chip.warn {{ border-color: rgba(245, 158, 11, 0.45); color: var(--warning); background: rgba(245, 158, 11, 0.08); }}

  table.data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
  table.data-table th {{
    text-align: left;
    font-family: var(--font-mono);
    font-size: 10px;
    color: var(--smoke);
    border-bottom: 1px solid var(--border);
    padding: 7px 8px;
    text-transform: uppercase;
  }}
  table.data-table td {{
    padding: 8px;
    border-bottom: 1px solid var(--border);
    color: var(--text);
    vertical-align: top;
  }}

  .btn-accent {{
    background: var(--accent);
    color: #0d1612;
    border: none;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    padding: 7px 12px;
    border-radius: 4px;
    cursor: pointer;
  }}
  .btn-accent:hover {{ background: var(--mint); }}
  .btn-ghost {{
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border-input);
    font-family: var(--font-mono);
    font-size: 11px;
    padding: 6px 10px;
    border-radius: 4px;
    cursor: pointer;
  }}
  .btn-ghost:hover {{ border-color: var(--accent); color: var(--accent); }}

  .propale-doc {{
    font-size: 13px;
    line-height: 1.6;
    color: var(--muted);
  }}
  .propale-doc h1 {{ font-size: 18px; color: var(--accent); border-bottom: 1px solid var(--border); padding-bottom: 6px; margin: 12px 0 10px; }}
  .propale-doc h2 {{ font-size: 14px; color: var(--text); margin: 14px 0 6px; font-family: var(--font-mono); }}
  .propale-doc h3 {{ font-size: 13px; color: var(--text); margin: 10px 0 4px; }}
  .propale-doc p {{ margin-bottom: 8px; }}
  .propale-doc ul {{ margin: 4px 0 10px 18px; }}
  .propale-doc li {{ margin-bottom: 4px; }}

  .patched-block {{
    margin-top: 12px;
    padding: 10px 12px;
    border-left: 3px solid var(--accent);
    background: rgba(62, 207, 142, 0.06);
    border-radius: 4px;
  }}

  .vuln-card {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 13px;
    margin-bottom: 10px;
  }}
  .vuln-card.resolved {{
    border-color: rgba(62, 207, 142, 0.5);
    background: rgba(62, 207, 142, 0.04);
  }}

  .patch-btn {{
    margin-top: 8px;
    background: var(--card);
    border: 1px solid var(--accent);
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 700;
    padding: 6px 11px;
    border-radius: 4px;
    cursor: pointer;
  }}
  .patch-btn:hover:not(:disabled) {{ background: var(--accent); color: #0d1612; }}
  .patch-btn:disabled {{
    border-color: rgba(62, 207, 142, 0.4);
    background: rgba(62, 207, 142, 0.1);
    cursor: default;
  }}

  .case-mini {{
    padding: 10px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    margin-bottom: 8px;
  }}

  .locked-panel {{
    max-width: 680px;
    margin: 48px auto;
    background: var(--card);
    border: 1px solid rgba(239, 68, 68, 0.5);
    border-radius: 8px;
    padding: 28px;
    text-align: center;
  }}
</style>
</head>
<body>
<div class="stage" id="stage">
  <header class="hud-bar">
    <div class="hud-brand">
      <span class="hud-dot"></span>
      <span>DELOITTE // SECURE BID SQUAD</span>
    </div>
    <div class="hud-metrics">
      <div class="hud-pill">IAM <strong id="hud-role"></strong></div>
      <div class="hud-pill accent">ROI: <strong>40h -> 6h (-85%)</strong></div>
      <div class="hud-pill">PII MASKED <strong id="hud-dlp"></strong></div>
      <div class="hud-pill" id="hud-gonogo-pill">GO / NO-GO <strong id="hud-gonogo"></strong></div>
      <div class="hud-pill accent" id="hud-redteam-pill">RED-TEAM SCORE <strong id="hud-redteam"></strong></div>
    </div>
  </header>

  <main class="shelf-viewport" id="viewport">
    <div class="shelf-track" id="shelf-track"></div>
    <div class="shelf-floor"></div>
  </main>

  <footer class="controls-bar">
    <div class="vol-pills" id="vol-pills"></div>
    <div class="nav-actions">
      <span class="nav-hint">Arrow Keys / Scroll · Click / Enter to open</span>
      <button class="nav-btn" id="btn-prev" type="button">◀</button>
      <button class="nav-btn" id="btn-next" type="button">▶</button>
      <button class="nav-btn primary" id="btn-open" type="button">OPEN / VIEW</button>
    </div>
  </footer>

  <div class="custom-cursor" id="custom-cursor">
    <span class="custom-cursor-label" id="cursor-label">OPEN / VIEW</span>
  </div>

  <section class="sheet-overlay" id="sheet-overlay" aria-hidden="true">
    <div class="sheet-topbar">
      <div class="sheet-title-group">
        <span class="sheet-vol-badge" id="sheet-vol"></span>
        <div>
          <div class="sheet-title" id="sheet-title"></div>
          <div class="sheet-subtitle" id="sheet-subtitle"></div>
        </div>
      </div>
      <div class="agent-strip" id="sheet-agent-strip">
        <span class="agent-pill">1. Strategist ✓</span>
        <span class="agent-pill">2. Knowledge ✓</span>
        <span class="agent-pill">3. ESG ✓</span>
        <span class="agent-pill">4. Architect ✓</span>
        <span class="agent-pill">5. Red-Team ✓</span>
      </div>
      <button class="sheet-close-btn" id="sheet-close" type="button">CLOSE / ESC</button>
    </div>
    <div class="sheet-body" id="sheet-body"></div>
  </section>
</div>

<script>
(() => {{
  const PAYLOAD = {payload_json};
  const THEME = {theme_json};
  const PROJECTS = PAYLOAD.projects || [];
  const N = PROJECTS.length;
  const REPEATS = 3;
  const TOTAL = N * REPEATS;
  const STRIDE = 108;
  const ACTIVE_GAP = 102;

  // Track applied Red-Team patches per project ID
  const projectPatches = {{}};
  PROJECTS.forEach(p => {{ projectPatches[p.id] = new Set(); }});

  function getGain(v) {{
    return Number(v.points_gain ?? v.penalty ?? 8);
  }}

  function getLiveRedTeamScore(proj) {{
    if (proj.is_locked) return 0;
    const base = Number(proj?.redteam?.initial_score ?? 74);
    const patchedSet = projectPatches[proj.id] || new Set();
    const vulns = proj?.redteam?.vulnerabilities || [];
    let bonus = 0;
    vulns.forEach(v => {{ if (patchedSet.has(v.id)) bonus += getGain(v); }});
    return Math.min(100, base + bonus);
  }}

  function getLivePropaleMarkdown(proj) {{
    let md = proj?.propale?.markdown || "# Structured Proposal\\n\\nPending generation.";
    const patchedSet = projectPatches[proj.id] || new Set();
    const vulns = proj?.redteam?.vulnerabilities || [];
    const patchedItems = vulns.filter(v => patchedSet.has(v.id));
    if (patchedItems.length > 0) {{
      md += "\\n\\n---\\n\\n## Red-Team Remediation Addenda\\n";
      patchedItems.forEach(v => {{
        md += `\\n### [PATCHED] ${{v.title}} (+${{getGain(v)}} pts)\\n${{v.patch_text}}\\n`;
      }});
    }}
    return md;
  }}

  function getCoverSvg(proj) {{
    if (proj.is_locked) {{
      return `<svg width="82" height="82" viewBox="0 0 82 82" fill="none">
        <rect x="21" y="36" width="40" height="30" rx="4" stroke="#ef4444" stroke-width="2.5"/>
        <path d="M29 36V26C29 19.4 34.4 14 41 14C47.6 14 53 19.4 53 26V36" stroke="#ef4444" stroke-width="2.5"/>
        <circle cx="41" cy="51" r="4" fill="#ef4444"/>
      </svg>`;
    }}
    const s = THEME.accent;
    return `<svg width="82" height="82" viewBox="0 0 82 82" fill="none">
      <polygon points="41,10 68,25 68,57 41,72 14,57 14,25" stroke="${{s}}" stroke-width="2.2"/>
      <circle cx="41" cy="41" r="14" stroke="#393939" stroke-width="2"/>
      <path d="M34 41L39 46L49 35" stroke="${{s}}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>`;
  }}

  const trackEl = document.getElementById("shelf-track");
  const slots = [];

  for (let i = 0; i < TOTAL; i++) {{
    const proj = PROJECTS[i % N];
    const slot = document.createElement("div");
    slot.className = "dossier-slot" + (proj.is_locked ? " is-locked" : "");
    slot.dataset.index = String(i);

    const statusTag = proj.is_locked ? "LOCKED // CHINESE WALL" : proj.badge;
    const kpiText = proj.is_locked
      ? "LOCKED // CHINESE WALL"
      : `${{proj.go_nogo?.decision || "GO"}} · ${{proj.go_nogo?.score || 84}}/100`;

    slot.innerHTML = `
      <div class="dossier-box">
        <div class="face-spine">
          <div class="spine-vol">${{proj.code}}</div>
          <div class="spine-title">${{proj.title}}</div>
          <div class="spine-footer">
            <div class="spine-code">${{proj.is_locked ? "LOCKED" : proj.budget}}</div>
            <div class="spine-bar"></div>
          </div>
        </div>
        <div class="face-cover">
          <div class="cover-grid-bg"></div>
          <div class="cover-top">
            <div class="cover-header-row">
              <span>${{proj.sector.toUpperCase()}}</span>
              <span class="cover-tag ${{proj.is_locked ? "locked" : ""}}">${{statusTag}}</span>
            </div>
            <div class="cover-vol">${{proj.code}} // ${{proj.year || "2026"}}</div>
            <div class="cover-title">${{proj.title}}</div>
            <div class="cover-client">${{proj.client}}</div>
            <div class="cover-meta-row">
              <span class="cover-chip">${{proj.budget}}</span>
              <span class="cover-chip">${{proj.deadline}}</span>
            </div>
          </div>
          <div class="cover-svg-wrap">${{getCoverSvg(proj)}}</div>
          <div class="cover-bottom">
            <span class="cover-kpi ${{proj.is_locked ? "locked" : ""}}" data-proj-kpi="${{proj.id}}">${{kpiText}}</span>
            <span class="cover-open-hint">${{proj.is_locked ? "RESTRICTED" : "OPEN"}}</span>
          </div>
        </div>
        <div class="face-left"></div>
        <div class="face-top"></div>
      </div>
    `;

    trackEl.appendChild(slot);
    slots.push({{ el: slot, box: slot.querySelector(".dossier-box"), cover: slot.querySelector(".face-cover"), proj, index: i }});
  }}

  const pillsWrap = document.getElementById("vol-pills");
  const pillButtons = PROJECTS.map((p, idx) => {{
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "vol-pill" + (p.is_locked ? " locked" : "");
    btn.textContent = `${{p.code}} · ${{p.is_locked ? "LOCKED" : p.badge}}`;
    btn.addEventListener("click", () => jumpToBaseIndex(idx));
    pillsWrap.appendChild(btn);
    return btn;
  }});

  // Start centered on Project 0 (LIVE RFP) in the middle repeat
  let currentPos = N;
  let targetPos = N;
  let activeSlotIndex = N;
  let mouseNormX = 0;
  let mouseNormY = 0;
  let isSheetOpen = false;
  let activeTab = "proposal";
  let proposalViewMode = "preview";

  function updateHudForProject(proj) {{
    document.getElementById("hud-role").textContent = PAYLOAD.clearance || "LEVEL 2";
    document.getElementById("hud-dlp").textContent = `${{proj?.dlp?.masked_count ?? 0}} items`;
    const gPill = document.getElementById("hud-gonogo-pill");
    const rPill = document.getElementById("hud-redteam-pill");
    if (proj.is_locked) {{
      document.getElementById("hud-gonogo").textContent = "LOCKED";
      document.getElementById("hud-redteam").textContent = "CHINESE WALL";
      gPill.className = "hud-pill danger";
      rPill.className = "hud-pill danger";
    }} else {{
      document.getElementById("hud-gonogo").textContent = `${{proj?.go_nogo?.score ?? 0}}/100`;
      document.getElementById("hud-redteam").textContent = `${{getLiveRedTeamScore(proj)}}/100`;
      gPill.className = "hud-pill";
      rPill.className = "hud-pill accent";
    }}
  }}

  function jumpToBaseIndex(baseIdx) {{
    const currentRound = Math.round(targetPos);
    const currentBase = ((currentRound % N) + N) % N;
    let delta = baseIdx - currentBase;
    if (delta > N / 2) delta -= N;
    if (delta < -N / 2) delta += N;
    targetPos = currentRound + delta;
  }}

  function normalizeLoop() {{
    if (currentPos < N * 0.5 && targetPos < N * 0.5) {{
      currentPos += N; targetPos += N;
    }} else if (currentPos > N * 2.3 && targetPos > N * 2.3) {{
      currentPos -= N; targetPos -= N;
    }}
  }}

  const slotStates = slots.map(() => ({{ rotY: 0, rotZ: 0, z: 0, tiltX: 0, tiltY: 0 }}));
  let lastHudBase = -1;

  function animate() {{
    currentPos += (targetPos - currentPos) * 0.12;
    normalizeLoop();

    const nearest = Math.round(currentPos);
    activeSlotIndex = Math.max(0, Math.min(TOTAL - 1, nearest));
    const activeBase = ((activeSlotIndex % N) + N) % N;

    if (activeBase !== lastHudBase) {{
      lastHudBase = activeBase;
      updateHudForProject(PROJECTS[activeBase]);
    }}

    pillButtons.forEach((btn, idx) => btn.classList.toggle("active", idx === activeBase));

    slots.forEach((s, i) => {{
      const dist = i - currentPos;
      const isAct = i === activeSlotIndex;
      s.el.classList.toggle("is-active", isAct);

      let gapOffset = 0;
      if (dist > 0.35) gapOffset = ACTIVE_GAP;
      else if (dist < -0.35) gapOffset = -ACTIVE_GAP;
      else gapOffset = dist * ACTIVE_GAP * 2.2;

      const x = dist * STRIDE + gapOffset;
      const st = slotStates[i];

      const goalRotY = isAct ? -90 : 0;
      const goalRotZ = isAct ? -4.5 : 0;
      const goalZ = isAct ? 138 : -Math.min(Math.abs(dist) * 14, 90);
      const goalTiltX = isAct ? -mouseNormY * 4.5 : 0;
      const goalTiltY = isAct ? mouseNormX * 5.5 : 0;

      st.rotY += (goalRotY - st.rotY) * 0.14;
      st.rotZ += (goalRotZ - st.rotZ) * 0.14;
      st.z += (goalZ - st.z) * 0.14;
      st.tiltX += (goalTiltX - st.tiltX) * 0.14;
      st.tiltY += (goalTiltY - st.tiltY) * 0.14;

      s.el.style.transform = `translate3d(${{x.toFixed(2)}}px, 0px, ${{st.z.toFixed(2)}}px)`;
      s.el.style.zIndex = String(isAct ? 100 : Math.max(1, 50 - Math.round(Math.abs(dist) * 4)));
      s.box.style.transform = `rotateX(${{st.tiltX.toFixed(2)}}deg) rotateY(${{(st.rotY + st.tiltY).toFixed(2)}}deg) rotateZ(${{st.rotZ.toFixed(2)}}deg)`;
    }});

    requestAnimationFrame(animate);
  }}
  requestAnimationFrame(animate);

  // Mouse & Custom Cursor
  const stageEl = document.getElementById("stage");
  const cursorEl = document.getElementById("custom-cursor");
  const cursorLabel = document.getElementById("cursor-label");

  function isPointInActiveCover(x, y, pad = 10) {{
    const activeSlot = slots[activeSlotIndex];
    if (!activeSlot || !activeSlot.cover) return false;
    const r = activeSlot.cover.getBoundingClientRect();
    return x >= r.left - pad && x <= r.right + pad && y >= r.top - pad && y <= r.bottom + pad;
  }}

  stageEl.addEventListener("mousemove", (e) => {{
    const rect = stageEl.getBoundingClientRect();
    mouseNormX = ((e.clientX - rect.left) / rect.width - 0.5) * 2;
    mouseNormY = ((e.clientY - rect.top) / rect.height - 0.5) * 2;

    if (isSheetOpen) {{ cursorEl.style.opacity = "0"; return; }}

    cursorEl.style.opacity = "1";
    cursorEl.style.left = `${{e.clientX}}px`;
    cursorEl.style.top = `${{e.clientY}}px`;

    const overCover = Boolean(e.target.closest(".dossier-slot.is-active .face-cover")) || isPointInActiveCover(e.clientX, e.clientY, 4);
    const overSpine = !overCover && Boolean(e.target.closest(".face-spine"));
    const overChrome = Boolean(e.target.closest(".hud-bar, .controls-bar"));

    if (overChrome) {{
      cursorEl.style.opacity = "0";
      cursorEl.classList.remove("on-cover", "on-spine", "locked");
    }} else if (overCover) {{
      const activeSlot = slots[activeSlotIndex];
      const isLocked = Boolean(activeSlot?.proj?.is_locked);
      cursorEl.classList.add("on-cover");
      cursorEl.classList.toggle("locked", isLocked);
      cursorEl.classList.remove("on-spine");
      cursorLabel.textContent = isLocked ? "LOCKED" : "OPEN / VIEW";
    }} else if (overSpine) {{
      cursorEl.classList.add("on-spine");
      cursorEl.classList.remove("on-cover", "locked");
    }} else {{
      cursorEl.classList.remove("on-cover", "on-spine", "locked");
    }}
  }});

  stageEl.addEventListener("mouseleave", () => {{ cursorEl.style.opacity = "0"; }});

  let wheelLock = 0;
  document.getElementById("viewport").addEventListener("wheel", (e) => {{
    if (isSheetOpen) return;
    e.preventDefault();
    const now = performance.now();
    if (now - wheelLock < 90) return;
    wheelLock = now;
    const delta = Math.abs(e.deltaY) > Math.abs(e.deltaX) ? e.deltaY : e.deltaX;
    if (delta > 10) targetPos = Math.round(targetPos) + 1;
    else if (delta < -10) targetPos = Math.round(targetPos) - 1;
  }}, {{ passive: false }});

  let pointerOrigin = null;
  const viewportEl = document.getElementById("viewport");
  viewportEl.addEventListener("pointerdown", (e) => {{
    if (isSheetOpen || e.button !== 0) return;
    pointerOrigin = {{ x: e.clientX, y: e.clientY, target: e.target }};
  }});
  window.addEventListener("pointerup", (e) => {{
    if (!pointerOrigin) return;
    const dx = e.clientX - pointerOrigin.x;
    const dy = e.clientY - pointerOrigin.y;
    const startTarget = pointerOrigin.target;
    pointerOrigin = null;

    if (isSheetOpen) return;

    // Horizontal swipe/drag turns the shelf
    if (Math.abs(dx) > 40) {{
      targetPos = Math.round(targetPos) + (dx < 0 ? 1 : -1);
      return;
    }}

    // Crisp tap/click detection (100% reliable despite 3D CSS transforms)
    if (Math.hypot(dx, dy) <= 14) {{
      if (isPointInActiveCover(e.clientX, e.clientY, 12)) {{
        const s = slots[activeSlotIndex];
        if (s) openSheetForSlot(s.el, s.proj);
        return;
      }}
      const clickedSlot = e.target.closest(".dossier-slot") || startTarget?.closest?.(".dossier-slot");
      if (clickedSlot) {{
        const idx = Number(clickedSlot.dataset.index);
        if (idx === activeSlotIndex || Math.abs(idx - targetPos) < 0.35) {{
          const s = slots[activeSlotIndex];
          if (s) openSheetForSlot(s.el, s.proj);
        }} else {{
          targetPos = idx;
        }}
      }}
    }}
  }});

  document.getElementById("btn-prev").addEventListener("click", () => {{ targetPos = Math.round(targetPos) - 1; }});
  document.getElementById("btn-next").addEventListener("click", () => {{ targetPos = Math.round(targetPos) + 1; }});
  document.getElementById("btn-open").addEventListener("click", () => {{
    const s = slots[activeSlotIndex];
    if (s) openSheetForSlot(s.el, s.proj);
  }});

  window.addEventListener("keydown", (e) => {{
    if (e.key === "Escape" && isSheetOpen) {{ closeSheet(); return; }}
    if (isSheetOpen) return;
    if (e.key === "ArrowRight") targetPos = Math.round(targetPos) + 1;
    else if (e.key === "ArrowLeft") targetPos = Math.round(targetPos) - 1;
    else if (e.key === "Enter") {{
      const s = slots[activeSlotIndex];
      if (s) openSheetForSlot(s.el, s.proj);
    }}
  }});

  const sheetEl = document.getElementById("sheet-overlay");
  const sheetBody = document.getElementById("sheet-body");
  let lastOpenedRect = null;

  function escHtml(str) {{
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }}

  function buildMiniGauge(score, label, color) {{
    const r = 34;
    const c = 2 * Math.PI * r;
    const clamped = Math.max(0, Math.min(100, Number(score) || 0));
    const offset = c - (clamped / 100) * c;
    return `
      <svg width="88" height="88" viewBox="0 0 88 88">
        <circle cx="44" cy="44" r="${{r}}" fill="none" stroke="#2e2e2e" stroke-width="7"/>
        <circle cx="44" cy="44" r="${{r}}" fill="none" stroke="${{color}}" stroke-width="7"
          stroke-dasharray="${{c.toFixed(1)}}" stroke-dashoffset="${{offset.toFixed(1)}}"
          stroke-linecap="round" transform="rotate(-90 44 44)"/>
        <text x="44" y="43" text-anchor="middle" fill="#fafafa" font-family="JetBrains Mono, monospace" font-size="18" font-weight="700">${{clamped}}</text>
        <text x="44" y="57" text-anchor="middle" fill="#898989" font-family="JetBrains Mono, monospace" font-size="8">${{label}}</text>
      </svg>
    `;
  }}

  function renderSimpleMarkdown(md) {{
    const lines = String(md || "").split(/\\r?\\n/);
    let html = "";
    let inList = false;
    let inPatched = false;
    for (const raw of lines) {{
      const line = raw.trimEnd();
      if (line.startsWith("### [PATCHED]")) {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        if (inPatched) html += "</div>";
        inPatched = true;
        html += `<div class="patched-block"><h3><span class="tag-chip accent">PATCHED</span> ${{escHtml(line.slice(14))}}</h3>`;
      }} else if (line.startsWith("### ")) {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        html += `<h3>${{escHtml(line.slice(4))}}</h3>`;
      }} else if (line.startsWith("## ")) {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        if (inPatched) {{ html += "</div>"; inPatched = false; }}
        html += `<h2>${{escHtml(line.slice(3))}}</h2>`;
      }} else if (line.startsWith("# ")) {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        html += `<h1>${{escHtml(line.slice(2))}}</h1>`;
      }} else if (line.startsWith("- ") || line.startsWith("* ")) {{
        if (!inList) {{ html += "<ul>"; inList = true; }}
        const formatted = escHtml(line.slice(2)).replace(/\\*\\*(.+?)\\*\\*/g, "<strong>$1</strong>");
        html += `<li>${{formatted}}</li>`;
      }} else if (line === "---") {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        html += `<hr style="border:none;border-top:1px solid #2e2e2e;margin:14px 0;" />`;
      }} else if (line.trim() === "") {{
        if (inList) {{ html += "</ul>"; inList = false; }}
      }} else {{
        if (inList) {{ html += "</ul>"; inList = false; }}
        const formatted = escHtml(line).replace(/\\*\\*(.+?)\\*\\*/g, "<strong>$1</strong>");
        html += `<p>${{formatted}}</p>`;
      }}
    }}
    if (inList) html += "</ul>";
    if (inPatched) html += "</div>";
    return html;
  }}

  function renderProjectWarRoom(proj) {{
    // IAM Chinese Wall Locked View
    if (proj.is_locked) {{
      sheetBody.innerHTML = `
        <div class="locked-panel">
          <div style="font-family:var(--font-mono);font-size:12px;font-weight:700;color:var(--danger);letter-spacing:0.1em;margin-bottom:10px;">
            ACCESS DENIED // IAM CHINESE WALL ACTIVE
          </div>
          <h2 style="font-size:20px;margin-bottom:10px;">${{escHtml(proj.title)}} (${{escHtml(proj.code)}})</h2>
          <p style="font-size:13px;color:var(--muted);line-height:1.6;margin-bottom:18px;">
            This bid dossier belongs to the <strong style="color:var(--text)">${{escHtml(proj.sector)}}</strong> sector (${{escHtml(proj.client)}}).
            Your current IAM profile (<strong style="color:var(--text)">${{escHtml(PAYLOAD.role_label)}} · ${{escHtml(PAYLOAD.clearance)}}</strong>)
            does not have clearance to inspect or reference this engagement.
          </p>
          <div style="background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:12px;font-family:var(--font-mono);font-size:11px;color:var(--muted);">
            REQUIRED CLEARANCE: <strong style="color:var(--accent)">Partner · Banking &amp; Finance (Full Access) — LEVEL 5 (ALL)</strong>
          </div>
        </div>
      `;
      return;
    }}

    const liveScore = getLiveRedTeamScore(proj);
    const patchedSet = projectPatches[proj.id] || new Set();
    const g = proj.go_nogo || {{}};
    const r = proj.rse || {{}};
    const c = proj.cases || {{}};
    const d = proj.dlp || {{}};
    const rt = proj.redteam || {{}};
    const dims = PAYLOAD.dimensions || [];
    const complianceRows = (PAYLOAD.compliance_template || []).map(row => {{
      const isPatched = row.status === "PATCH_NEEDED" && patchedSet.size > 0;
      return {{
        ...row,
        displayStatus: isPatched ? "COVERED [PATCHED]" : row.status,
      }};
    }});

    const liveMd = getLivePropaleMarkdown(proj);

    let primaryHtml = "";
    if (activeTab === "proposal") {{
      primaryHtml = `
        <div class="panel">
          <div class="panel-title">
            <span>COMPLIANCE MATRIX (${{complianceRows.length}} MANDATORY REQUIREMENTS)</span>
            <span class="tag-chip accent">${{patchedSet.size}} PATCH(ES) APPLIED</span>
          </div>
          <table class="data-table">
            <thead><tr><th>REQ ID</th><th>Requirement</th><th>Deloitte Response</th><th>Status</th></tr></thead>
            <tbody>
              ${{complianceRows.map(row => {{
                const isCov = row.displayStatus.startsWith("COVERED");
                return `<tr>
                  <td style="font-family:var(--font-mono);color:var(--accent);">${{escHtml(row.id)}}</td>
                  <td>${{escHtml(row.requirement)}}</td>
                  <td style="color:var(--muted);">${{escHtml(row.deloitte_response)}}</td>
                  <td><span class="tag-chip ${{isCov ? "accent" : "warn"}}">${{escHtml(row.displayStatus)}}</span></td>
                </tr>`;
              }}).join("")}}
            </tbody>
          </table>
        </div>
        <div class="panel">
          <div class="panel-title">
            <span>STRUCTURED PROPOSAL DELIVERABLE</span>
            <div style="display:flex;gap:8px;align-items:center;">
              <button class="btn-ghost" id="btn-toggle-md" type="button">
                ${{proposalViewMode === "preview" ? "Source (.md)" : "Preview"}}
              </button>
              <button class="btn-accent" id="btn-dl-md" type="button">Download Proposal (.md)</button>
            </div>
          </div>
          ${{proposalViewMode === "preview"
            ? `<div class="propale-doc">${{renderSimpleMarkdown(liveMd)}}</div>`
            : `<pre style="white-space:pre-wrap;font-family:var(--font-mono);font-size:11px;color:var(--muted);background:var(--bg);padding:14px;border-radius:4px;border:1px solid var(--border);">${{escHtml(liveMd)}}</pre>`
          }}
        </div>
      `;
    }} else if (activeTab === "redteam") {{
      const vulns = rt.vulnerabilities || [];
      const passed = rt.controles_passes || [];
      primaryHtml = `
        <div class="panel">
          <div class="panel-title">
            <span>BUYER PERSONA CRITIQUE &amp; PASSED DEFENSES</span>
            <span class="tag-chip ${{liveScore >= 90 ? "accent" : "warn"}}">Readiness: ${{liveScore}}/100</span>
          </div>
          <p style="font-size:13px;color:var(--muted);margin-bottom:10px;">${{escHtml(rt.summary || "")}}</p>
          <div style="display:flex;gap:6px;flex-wrap:wrap;">
            ${{passed.map(p => `<span class="tag-chip accent">✓ ${{escHtml(p)}}</span>`).join("")}}
          </div>
        </div>
        <div class="panel">
          <div class="panel-title">CRITICAL GAPS &amp; ONE-CLICK AI REMEDIATION (${{vulns.length}})</div>
          ${{vulns.map(v => {{
            const isRes = patchedSet.has(v.id);
            const gain = getGain(v);
            return `
              <div class="vuln-card ${{isRes ? "resolved" : ""}}">
                <div style="display:flex;justify-content:space-between;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;">
                  <strong style="font-size:13px;">
                    ${{isRes ? '<span class="tag-chip accent">[RESOLVED]</span> ' : '<span class="tag-chip danger">[GAP]</span> '}}
                    ${{escHtml(v.title)}}
                  </strong>
                  <span class="tag-chip ${{isRes ? "accent" : "danger"}}">${{isRes ? "+" : "-"}} ${{gain}} pts</span>
                </div>
                <p style="font-size:12px;color:var(--muted);margin-bottom:8px;">${{escHtml(v.critique)}}</p>
                <details style="margin-bottom:6px;">
                  <summary style="font-family:var(--font-mono);font-size:11px;color:var(--accent);cursor:pointer;">Inspect AI Patch Clause</summary>
                  <pre style="white-space:pre-wrap;font-family:var(--font-mono);font-size:11px;color:var(--muted);background:var(--bg);padding:10px;border-radius:4px;margin-top:6px;border:1px solid var(--border);">${{escHtml(v.patch_text)}}</pre>
                </details>
                <button class="patch-btn" type="button" data-patch-id="${{escHtml(v.id)}}" ${{isRes ? "disabled" : ""}}>
                  ${{isRes ? "[RESOLVED] Injected into Proposal" : `Apply Fix (+${{gain}} pts)`}}
                </button>
              </div>
            `;
          }}).join("")}}
        </div>
      `;
    }} else {{
      const reqs = g.requirements || [];
      const risks = g.risks || [];
      primaryHtml = `
        <div class="panel">
          <div class="panel-title">STRATEGIST ANALYST SUMMARY</div>
          <p style="font-size:13px;color:var(--muted);line-height:1.6;margin-bottom:10px;">${{escHtml(g.summary || "")}}</p>
          <ul style="margin-left:18px;font-size:12px;color:var(--text);line-height:1.6;">
            ${{reqs.map(rq => `<li>${{escHtml(rq.title || rq)}}</li>`).join("")}}
          </ul>
        </div>
        <div class="panel">
          <div class="panel-title">RISK &amp; MITIGATION MATRIX</div>
          <table class="data-table">
            <thead><tr><th>Risk</th><th>Severity</th><th>Mitigation Strategy</th></tr></thead>
            <tbody>
              ${{risks.map(rk => `<tr>
                <td>${{escHtml(rk.title)}}</td>
                <td><span class="tag-chip warn">${{escHtml(rk.severity)}}</span></td>
                <td style="color:var(--muted);">${{escHtml(rk.mitigation)}}</td>
              </tr>`).join("")}}
            </tbody>
          </table>
        </div>
      `;
    }}

    sheetBody.innerHTML = `
      <!-- Executive Intelligence Strip (3 smart cards) -->
      <div class="exec-strip">
        <div class="panel">
          <div class="panel-title">
            <span>GO / NO-GO DECISION</span>
            <span class="tag-chip accent">${{escHtml(g.decision || "GO")}} · ${{g.score ?? 86}}/100</span>
          </div>
          ${{dims.map(dim => `
            <div class="dim-row">
              <span>${{escHtml(dim.label)}}</span>
              <div style="display:flex;align-items:center;gap:6px;">
                <div class="dim-bar-bg"><div class="dim-bar-fill" style="width:${{dim.base}}%;"></div></div>
                <span style="font-family:var(--font-mono);color:var(--text);">${{dim.base}}</span>
              </div>
            </div>
          `).join("")}}
        </div>

        <div class="panel" style="display:flex;align-items:center;gap:14px;">
          ${{buildMiniGauge(r.score ?? 92, "CSRD", THEME.accent)}}
          <div>
            <div class="panel-title" style="margin-bottom:4px;">ESG &amp; LOW-CARBON</div>
            <div style="font-family:var(--font-mono);font-size:11px;color:var(--accent);margin-bottom:4px;">GCP ${{escHtml(r.region || "europe-west9")}}</div>
            <div style="font-size:12px;color:var(--muted);">~50 gCO2eq/kWh · CSRD Scope 2/3 &amp; RGESN aligned</div>
          </div>
        </div>

        <div class="panel" style="display:flex;align-items:center;gap:14px;">
          ${{buildMiniGauge(liveScore, "READY", liveScore >= 90 ? THEME.accent : THEME.warning)}}
          <div>
            <div class="panel-title" style="margin-bottom:4px;">RED-TEAM READINESS</div>
            <div style="font-family:var(--font-mono);font-size:12px;color:var(--text);margin-bottom:4px;">
              Initial: ${{rt.initial_score ?? 74}} -> Live: <strong style="color:var(--accent);">${{liveScore}}/100</strong>
            </div>
            <div style="font-size:12px;color:var(--muted);">${{(rt.vulnerabilities || []).length - patchedSet.size}} open gap(s) remaining</div>
          </div>
        </div>
      </div>

      <!-- Prioritized 2-Column War Room (64% Left | 36% Right) -->
      <div class="warroom-grid">
        <div class="primary-col">
          <div class="seg-bar">
            <div class="seg-tabs">
              <button class="seg-btn ${{activeTab === "proposal" ? "active" : ""}}" data-tab="proposal" type="button">Proposal &amp; Compliance</button>
              <button class="seg-btn ${{activeTab === "redteam" ? "active" : ""}}" data-tab="redteam" type="button">Red-Team War Room (${{(rt.vulnerabilities || []).length - patchedSet.size}})</button>
              <button class="seg-btn ${{activeTab === "gonogo" ? "active" : ""}}" data-tab="gonogo" type="button">Go/No-Go &amp; Risks</button>
            </div>
            <span style="font-family:var(--font-mono);font-size:10px;color:var(--smoke);">PRIMARY WORKSPACE</span>
          </div>
          ${{primaryHtml}}
        </div>

        <aside class="supporting-col">
          <div class="panel">
            <div class="panel-title">
              <span>CLOUD DLP AIRLOCK LOG</span>
              <span class="tag-chip accent">ZERO PII LEAK</span>
            </div>
            <div style="font-size:12px;color:var(--muted);margin-bottom:8px;">
              <strong style="color:var(--text);">${{d.masked_count ?? 0}} sensitive items</strong> masked before LLM inference:
            </div>
            <div style="display:flex;gap:6px;flex-wrap:wrap;">
              ${{(d.details || []).map(dt => `<span class="tag-chip">${{escHtml(dt.info_type)}}: ${{dt.count}}</span>`).join("") || '<span class="tag-chip accent">Clean input</span>'}}
            </div>
          </div>

          <div class="panel">
            <div class="panel-title">
              <span>SOURCED CLIENT CASES (IAM)</span>
              <span class="tag-chip">${{(c.items || []).length}} CASES</span>
            </div>
            ${{(c.blocked_sectors || []).length > 0
              ? `<div style="font-family:var(--font-mono);font-size:10px;color:var(--warning);margin-bottom:8px;">Chinese Wall filtered: ${{escHtml(c.blocked_sectors.join(", "))}}</div>`
              : ""}}
            ${{(c.items || []).map(item => `
              <div class="case-mini">
                <div style="display:flex;justify-content:space-between;gap:6px;margin-bottom:4px;">
                  <span class="tag-chip accent">${{escHtml(item.sector)}}</span>
                  <span style="font-family:var(--font-mono);font-size:10px;color:var(--smoke);">${{escHtml(item.source)}}</span>
                </div>
                <div style="font-size:12px;font-weight:600;color:var(--text);margin-bottom:3px;">${{escHtml(item.title)}}</div>
                <div style="font-size:11px;color:var(--muted);line-height:1.45;">${{escHtml(item.summary)}}</div>
              </div>
            `).join("")}}
          </div>

          <div class="panel">
            <div class="panel-title">ESG &amp; GREENOPS DIFFERENTIATORS</div>
            <ul style="margin-left:16px;font-size:12px;color:var(--muted);line-height:1.6;">
              ${{(r.low_carbon_args || []).map(a => `<li>${{escHtml(a)}}</li>`).join("")}}
            </ul>
          </div>
        </aside>
      </div>
    `;

    // Bind Tab Switcher
    sheetBody.querySelectorAll(".seg-btn").forEach(btn => {{
      btn.addEventListener("click", () => {{
        activeTab = btn.getAttribute("data-tab");
        renderProjectWarRoom(proj);
      }});
    }});

    // Bind Proposal Preview/Source & Download
    const toggleBtn = document.getElementById("btn-toggle-md");
    if (toggleBtn) {{
      toggleBtn.addEventListener("click", () => {{
        proposalViewMode = proposalViewMode === "preview" ? "source" : "preview";
        renderProjectWarRoom(proj);
      }});
    }}
    const dlBtn = document.getElementById("btn-dl-md");
    if (dlBtn) {{
      dlBtn.addEventListener("click", () => {{
        const blob = new Blob([getLivePropaleMarkdown(proj)], {{ type: "text/markdown;charset=utf-8" }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `${{proj.code.toLowerCase()}}_proposal.md`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        URL.revokeObjectURL(url);
      }});
    }}

    // Bind Red-Team Patch Buttons
    sheetBody.querySelectorAll(".patch-btn").forEach(btn => {{
      btn.addEventListener("click", () => {{
        const vid = btn.getAttribute("data-patch-id");
        projectPatches[proj.id].add(vid);
        updateHudForProject(proj);
        renderProjectWarRoom(proj);
      }});
    }});
  }}

  function openSheetForSlot(slotEl, proj) {{
    if (isSheetOpen) return;
    isSheetOpen = true;
    activeTab = "proposal";
    proposalViewMode = "preview";
    cursorEl.style.opacity = "0";

    const coverEl = slotEl.querySelector(".face-cover");
    const rect = coverEl ? coverEl.getBoundingClientRect() : slotEl.getBoundingClientRect();
    lastOpenedRect = rect;

    document.getElementById("sheet-vol").textContent = `${{proj.code}} // ${{proj.sector.toUpperCase()}}`;
    document.getElementById("sheet-title").textContent = proj.title;
    document.getElementById("sheet-subtitle").textContent = `${{proj.client}} · ${{proj.budget}} · ${{proj.deadline}} · ${{PAYLOAD.clearance}}`;
    document.getElementById("sheet-agent-strip").style.display = proj.is_locked ? "none" : "flex";

    renderProjectWarRoom(proj);

    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const top = Math.max(0, rect.top);
    const left = Math.max(0, rect.left);
    const right = Math.max(0, vw - rect.right);
    const bottom = Math.max(0, vh - rect.bottom);

    sheetEl.classList.add("is-open");
    sheetEl.setAttribute("aria-hidden", "false");
    sheetEl.animate(
      [
        {{ clipPath: `inset(${{top}}px ${{right}}px ${{bottom}}px ${{left}}px round 6px)`, opacity: 0.75 }},
        {{ clipPath: "inset(0px 0px 0px 0px round 0px)", opacity: 1 }},
      ],
      {{ duration: 360, easing: "cubic-bezier(0.22, 1, 0.36, 1)", fill: "forwards" }}
    );
  }}

  function closeSheet() {{
    if (!isSheetOpen) return;
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const rect = lastOpenedRect || {{ top: vh / 2 - 100, left: vw / 2 - 80, right: vw / 2 + 80, bottom: vh / 2 + 100 }};
    const top = Math.max(0, rect.top);
    const left = Math.max(0, rect.left);
    const right = Math.max(0, vw - rect.right);
    const bottom = Math.max(0, vh - rect.bottom);

    const anim = sheetEl.animate(
      [
        {{ clipPath: "inset(0px 0px 0px 0px round 0px)", opacity: 1 }},
        {{ clipPath: `inset(${{top}}px ${{right}}px ${{bottom}}px ${{left}}px round 6px)`, opacity: 0 }},
      ],
      {{ duration: 260, easing: "cubic-bezier(0.4, 0, 0.2, 1)", fill: "forwards" }}
    );
    anim.onfinish = () => {{
      sheetEl.classList.remove("is-open");
      sheetEl.setAttribute("aria-hidden", "true");
      isSheetOpen = false;
    }};
  }}

  document.getElementById("sheet-close").addEventListener("click", closeSheet);
}})();
</script>
</body>
</html>"""
