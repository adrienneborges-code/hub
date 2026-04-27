// Shared auth, navigation, and utility functions for Adrienne's Sales Hub

const AUTH_KEY = 'hub_auth_ts';
const AUTH_TTL = 8 * 60 * 60 * 1000; // 8 hours

function isAuthed() {
  const ts = localStorage.getItem(AUTH_KEY);
  if (!ts) return false;
  return Date.now() - parseInt(ts) < AUTH_TTL;
}

function setAuthed() {
  localStorage.setItem(AUTH_KEY, Date.now().toString());
}

function requireAuth() {
  if (!isAuthed()) {
    // All protected pages are exactly one level deep (dashboard/, deal-review/, map-hub/)
    window.location.href = '../index.html?redirect=' + encodeURIComponent(location.href);
  }
}

function logout() {
  localStorage.removeItem(AUTH_KEY);
  window.location.href = '../index.html';
}

// Format currency
function fmt$(n) {
  if (!n) return '$0';
  if (n >= 1000000) return '$' + (n/1000000).toFixed(1) + 'M';
  if (n >= 1000) return '$' + Math.round(n/1000) + 'K';
  return '$' + n.toLocaleString();
}

// Format date as "Apr 27"
function fmtDate(d) {
  if (!d) return '—';
  const dt = new Date(d + 'T00:00:00');
  return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Days until date
function daysUntil(dateStr) {
  if (!dateStr) return null;
  const diff = new Date(dateStr + 'T00:00:00') - new Date();
  return Math.ceil(diff / (1000 * 60 * 60 * 24));
}

// Days since date
function daysSince(dateStr) {
  if (!dateStr) return 999;
  const diff = new Date() - new Date(dateStr + 'T00:00:00');
  return Math.floor(diff / (1000 * 60 * 60 * 24));
}

// Current quarter label
function currentQuarter() {
  const today = new Date();
  for (const q of HUB_CONFIG.quarters) {
    if (today >= new Date(q.start) && today <= new Date(q.end)) return q;
  }
  return HUB_CONFIG.quarters[0];
}

// Stage color
const STAGE_COLORS = {
  'Discovery': '#6366f1',
  'Demo': '#8b5cf6',
  'Evaluation': '#f59e0b',
  'Negotiation': '#ef4444',
  'Closed Won': '#10b981',
  'Closed Lost': '#6b7280',
  'Prospect': '#94a3b8'
};

function stageColor(stage) {
  return STAGE_COLORS[stage] || '#94a3b8';
}

// Forecast category badge color
const FC_COLORS = {
  'Commit': '#10b981',
  'Best Case': '#f59e0b',
  'Pipeline': '#6366f1',
  'Omitted': '#6b7280'
};

function fcColor(fc) {
  return FC_COLORS[fc] || '#94a3b8';
}

// Total pipeline ARR
function pipelineTotal() {
  return PIPELINE_DEALS.reduce((s, d) => s + (d.amount || 0), 0);
}

// Weighted pipeline
function weightedPipeline() {
  return PIPELINE_DEALS.reduce((s, d) => s + ((d.amount || 0) * (d.probability || 0) / 100), 0);
}

// Copy to clipboard
function copyToClipboard(text) {
  navigator.clipboard.writeText(text).then(() => {
    const el = document.createElement('div');
    el.textContent = 'Copied!';
    el.style.cssText = 'position:fixed;bottom:24px;right:24px;background:#10b981;color:#fff;padding:8px 16px;border-radius:8px;font-size:14px;z-index:9999;';
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 2000);
  });
}

// Open Salesforce record
function openSF(sfId) {
  if (!sfId) return;
  window.open(HUB_CONFIG.sfUrl + '/' + sfId, '_blank');
}
