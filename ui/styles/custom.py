"""DVA Platform UI — Custom Styles."""

CUSTOM_CSS = """
:root {
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --transition: all 0.2s ease;
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --radius-sm: 4px;
  --radius: 8px;
  --radius-lg: 12px;
}

* {
  font-family: var(--font-family);
}

body {
  margin: 0;
  padding: 0;
  font-size: 14px;
  line-height: 1.5;
}

.q-page-container {
  padding-top: 0 !important;
}

/* --- Navigation --- */

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: var(--transition);
  font-size: 13px;
  user-select: none;
}

.nav-item:hover {
  background: var(--bg-hover);
}

.nav-item.active {
  background: var(--accent);
  color: #fff;
  font-weight: 500;
}

.nav-item.disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.nav-section-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 12px 16px 4px;
  opacity: 0.6;
  font-weight: 600;
}

/* --- Cards --- */

.workspace-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 20px;
  transition: var(--transition);
}

.workspace-card:hover {
  box-shadow: var(--shadow);
  border-color: var(--accent);
}

.card-hover {
  transition: var(--transition);
}

.card-hover:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* --- Status Badges --- */

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}

.status-badge.success { background: #e8f5e9; color: #2e7d32; }
.status-badge.warning { background: #fff3e0; color: #e65100; }
.status-badge.error { background: #ffebee; color: #c62828; }
.status-badge.info { background: #e3f2fd; color: #1565c0; }

.badge-light {
  background: #f5f5f5;
  color: #616161;
  border: 1px solid #e0e0e0;
}

.badge-dark {
  background: #424242;
  color: #fff;
  border: 1px solid #616161;
}

/* --- Metric Cards --- */

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  text-align: center;
  min-width: 120px;
  transition: var(--transition);
}

.metric-card:hover {
  box-shadow: var(--shadow);
}

.metric-value {
  font-size: 24px;
  font-weight: 700;
  font-family: var(--font-mono);
  color: var(--accent);
}

.metric-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

/* --- Section Header --- */

.section-header {
  font-size: 16px;
  font-weight: 600;
  padding: 8px 0;
  border-bottom: 2px solid var(--accent);
  margin-bottom: 12px;
}

/* --- Notification Banners --- */

.notification-banner {
  padding: 10px 16px;
  border-radius: var(--radius-sm);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.notification-banner.success { background: #e8f5e9; color: #2e7d32; border-left: 3px solid #4caf50; }
.notification-banner.warning { background: #fff3e0; color: #e65100; border-left: 3px solid #ff9800; }
.notification-banner.error { background: #ffebee; color: #c62828; border-left: 3px solid #f44336; }
.notification-banner.info { background: #e3f2fd; color: #1565c0; border-left: 3px solid #2196f3; }

/* --- Toolbar --- */

.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

/* --- Empty State --- */

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-secondary);
  text-align: center;
}

.empty-state-icon {
  font-size: 48px;
  color: #bdbdbd;
  margin-bottom: 8px;
}

/* --- Loading State --- */

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255,255,255,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

/* --- Buttons --- */

.btn-primary {
  font-weight: 500;
  letter-spacing: 0.3px;
}

.btn-secondary {
  font-weight: 500;
}

.btn-danger {
  font-weight: 500;
}

/* --- Input Fields --- */

.input-field {
  font-size: 14px;
}

/* --- Dialog --- */

.dialog-panel {
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 32px rgba(0,0,0,0.12);
}

/* --- Tooltips --- */

.tooltip-custom {
  font-size: 12px;
  background: #333;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  max-width: 250px;
}

/* --- Context Menu --- */

.context-menu {
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: var(--radius);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  padding: 4px 0;
  min-width: 160px;
}

/* --- Keyboard Shortcuts --- */

.keyboard-shortcut {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 6px;
  background: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 11px;
  color: #616161;
}

/* --- Guidance Card --- */

.guidance-card {
  border-radius: var(--radius);
  border-left: 3px solid var(--accent);
}

/* --- Step Indicator --- */

.step-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* --- Spacing Utilities --- */

.gap-xs { gap: 4px; }
.gap-sm { gap: 8px; }
.gap-md { gap: 16px; }
.gap-lg { gap: 24px; }
.gap-xl { gap: 32px; }

.mt-xs { margin-top: 4px; }
.mt-sm { margin-top: 8px; }
.mt-md { margin-top: 16px; }
.mt-lg { margin-top: 24px; }
.mt-xl { margin-top: 32px; }

.mb-xs { margin-bottom: 4px; }
.mb-sm { margin-bottom: 8px; }
.mb-md { margin-bottom: 16px; }
.mb-lg { margin-bottom: 24px; }

.p-xs { padding: 4px; }
.p-sm { padding: 8px; }
.p-md { padding: 16px; }
.p-lg { padding: 24px; }

/* --- Typography Improvements --- */

.text-xs { font-size: 11px; }
.text-sm { font-size: 13px; }
.text-base { font-size: 14px; }
.text-lg { font-size: 16px; }
.text-xl { font-size: 20px; }
.text-2xl { font-size: 24px; }
.text-3xl { font-size: 30px; }

/* --- Error/Success Banners --- */

.error-banner {
  background: #ffebee;
  color: #c62828;
  border: 1px solid #ef9a9a;
  border-radius: var(--radius);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.success-banner {
  background: #e8f5e9;
  color: #2e7d32;
  border: 1px solid #a5d6a7;
  border-radius: var(--radius);
  padding: 12px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* --- Table Styles --- */

.table-striped tbody tr:nth-child(even) {
  background: #fafafa;
}

.table-hover tbody tr:hover {
  background: #f0f0f0;
}

/* --- Progress Bar --- */

.progress-bar {
  height: 6px;
  border-radius: 3px;
  background: #e0e0e0;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}
"""
