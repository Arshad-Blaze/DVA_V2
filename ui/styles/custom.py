"""DVA Platform UI — Custom Styles."""

CUSTOM_CSS = """
:root {
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  --transition: all 0.2s ease;
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

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 16px;
  text-align: center;
  min-width: 120px;
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

.section-header {
  font-size: 16px;
  font-weight: 600;
  padding: 8px 0;
  border-bottom: 2px solid var(--accent);
  margin-bottom: 12px;
}

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

.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-secondary);
  text-align: center;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}
"""
