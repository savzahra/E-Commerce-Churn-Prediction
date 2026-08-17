// Dashboard chart logic — emerald theme
const TOOLTIP_BASE = {
  backgroundColor: 'rgba(22,27,34,0.96)',
  borderColor: 'rgba(255,255,255,0.07)',
  borderWidth: 1,
  titleColor: '#e6edf3',
  bodyColor: '#8b949e',
  padding: 10,
  cornerRadius: 6,
};

const GRID_COLOR  = 'rgba(255,255,255,0.05)';
const TICK_COLOR  = '#8b949e';
const TICK_FONT   = { size: 11 };

const SCALE_DEFAULTS = {
  x: { ticks: { color: TICK_COLOR, font: TICK_FONT }, grid: { color: GRID_COLOR } },
  y: { ticks: { color: TICK_COLOR, font: TICK_FONT }, grid: { color: GRID_COLOR } },
};

let charts = {};

function destroyChart(id) {
  if (charts[id]) { charts[id].destroy(); delete charts[id]; }
}

// ─── Donut ──────────────────────────────────────────────────
function renderDonut(data) {
  destroyChart('donut');
  const total = data.values[0] + data.values[1];
  const pct   = total > 0 ? ((data.values[0] / total) * 100).toFixed(1) : '0.0';
  document.getElementById('donutPct').textContent        = pct + '%';
  document.getElementById('legendChurn').textContent    = data.values[0].toLocaleString();
  document.getElementById('legendNonChurn').textContent = data.values[1].toLocaleString();

  charts['donut'] = new Chart(
    document.getElementById('chartDonut').getContext('2d'), {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.values,
          backgroundColor: ['rgba(248,113,113,0.8)', 'rgba(16,185,129,0.7)'],
          borderColor:     ['#f87171', '#10b981'],
          borderWidth: 2,
          hoverOffset: 5,
        }]
      },
      options: {
        cutout: '68%',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            ...TOOLTIP_BASE,
            callbacks: {
              label: ctx => ` ${ctx.label}: ${ctx.raw.toLocaleString()} (${total > 0 ? (ctx.raw/total*100).toFixed(1) : 0}%)`
            }
          }
        }
      }
    }
  );
}

// ─── Prob Distribution ──────────────────────────────────────
function renderProbDist(data) {
  destroyChart('probDist');
  charts['probDist'] = new Chart(
    document.getElementById('chartProbDist').getContext('2d'), {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Pelanggan',
          data: data.values,
          backgroundColor: data.labels.map((_, i) => {
            const p = i / 10;
            if (p >= 0.7) return 'rgba(248,113,113,0.75)';
            if (p >= 0.3) return 'rgba(245,158,11,0.75)';
            return 'rgba(16,185,129,0.75)';
          }),
          borderRadius: 4,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { display: false }, tooltip: TOOLTIP_BASE },
        scales: SCALE_DEFAULTS,
      }
    }
  );
}

// ─── Tenure (stacked bar) ───────────────────────────────────
function renderTenureChart(data) {
  destroyChart('tenure');
  charts['tenure'] = new Chart(
    document.getElementById('chartTenure').getContext('2d'), {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Churn',
            data: data.churn,
            backgroundColor: 'rgba(248,113,113,0.75)',
            borderRadius: 4,
          },
          {
            label: 'Non-Churn',
            data: data.total.map((t, i) => t - data.churn[i]),
            backgroundColor: 'rgba(16,185,129,0.45)',
            borderRadius: 4,
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#8b949e', font: { size: 11 }, boxWidth: 10, padding: 12 } },
          tooltip: TOOLTIP_BASE,
        },
        scales: {
          x: { ...SCALE_DEFAULTS.x, stacked: true },
          y: { ...SCALE_DEFAULTS.y, stacked: true },
        },
      }
    }
  );
}

// ─── Category (horizontal bar) ──────────────────────────────
function renderCategoryChart(data) {
  destroyChart('category');
  const churnRates = data.total.map((t, i) => t > 0 ? +(data.churn[i] / t * 100).toFixed(1) : 0);

  charts['category'] = new Chart(
    document.getElementById('chartCategory').getContext('2d'), {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Churn Rate (%)',
          data: churnRates,
          backgroundColor: 'rgba(16,185,129,0.6)',
          borderColor: '#10b981',
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { ...TOOLTIP_BASE, callbacks: { label: ctx => ` Churn Rate: ${ctx.raw}%` } }
        },
        scales: SCALE_DEFAULTS,
      }
    }
  );
}

// ─── Marital (grouped bar) ──────────────────────────────────
function renderMaritalChart(data) {
  destroyChart('marital');
  const palette = ['rgba(248,113,113,0.75)', 'rgba(251,191,36,0.75)', 'rgba(129,140,248,0.75)'];

  charts['marital'] = new Chart(
    document.getElementById('chartMarital').getContext('2d'), {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Churn',
            data: data.churn,
            backgroundColor: data.labels.map((_, i) => palette[i % palette.length]),
            borderRadius: 4,
          },
          {
            label: 'Non-Churn',
            data: data.total.map((t, i) => t - data.churn[i]),
            backgroundColor: 'rgba(255,255,255,0.06)',
            borderRadius: 4,
          }
        ]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#8b949e', font: { size: 11 }, boxWidth: 10 } },
          tooltip: TOOLTIP_BASE,
        },
        scales: {
          x: { ...SCALE_DEFAULTS.x, stacked: true },
          y: { ...SCALE_DEFAULTS.y, stacked: true },
        },
      }
    }
  );
}

// ─── Payment ────────────────────────────────────────────────
function renderPaymentChart(data) {
  destroyChart('payment');
  const churnRates = data.total.map((t, i) => t > 0 ? +(data.churn[i] / t * 100).toFixed(1) : 0);
  const palette = [
    'rgba(88,166,255,0.7)', 'rgba(16,185,129,0.7)', 'rgba(248,113,113,0.7)',
    'rgba(251,191,36,0.7)', 'rgba(129,140,248,0.7)'
  ];

  charts['payment'] = new Chart(
    document.getElementById('chartPayment').getContext('2d'), {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Churn Rate (%)',
          data: churnRates,
          backgroundColor: data.labels.map((_, i) => palette[i % palette.length]),
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { ...TOOLTIP_BASE, callbacks: { label: ctx => ` Churn Rate: ${ctx.raw}%` } }
        },
        scales: SCALE_DEFAULTS,
      }
    }
  );
}

// ─── Fetch & Filter ─────────────────────────────────────────
function _getFilterParams() {
  return {
    gender:         document.getElementById('filterGender')?.value    || '',
    city_tier:      document.getElementById('filterCityTier')?.value  || '',
    marital_status: document.getElementById('filterMarital')?.value   || '',
    tenure_min:     document.getElementById('filterTenureMin')?.value || '',
    tenure_max:     document.getElementById('filterTenureMax')?.value || '',
  };
}

async function loadSummary(params = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== '' && v !== null && v !== undefined) qs.append(k, v);
  });

  const res  = await fetch('/api/insight/summary?' + qs.toString());
  const data = await res.json();

  document.getElementById('metricTotal').textContent     = data.total_customers.toLocaleString();
  document.getElementById('metricChurn').textContent     = data.total_churn.toLocaleString();
  document.getElementById('metricChurnRate').textContent = data.churn_rate + '%';
  document.getElementById('metricHighRisk').textContent  = data.high_risk_count.toLocaleString();

  const metricTotalSub = document.getElementById('metricTotalSub');
  if (metricTotalSub) metricTotalSub.textContent = data.total_customers > 0
    ? `${data.low_risk_count} Low · ${data.medium_risk_count} Medium`
    : 'Belum ada prediksi';

  const empty  = document.getElementById('emptyState');
  const charts = document.getElementById('chartSection');
  const isEmpty = data.total_customers === 0;
  if (empty)  empty.style.display  = isEmpty ? 'block' : 'none';
  if (charts) charts.style.display = isEmpty ? 'none'  : 'block';
}

async function loadCharts(params = {}) {
  const qs = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== '' && v !== null && v !== undefined) qs.append(k, v);
  });

  const res  = await fetch('/api/insight/charts?' + qs.toString());
  const data = await res.json();

  renderDonut(data.churn_distribution);
  renderProbDist(data.prob_distribution);
  renderTenureChart(data.churn_by_tenure);
  renderCategoryChart(data.churn_by_category);
  renderMaritalChart(data.churn_by_marital);
  renderPaymentChart(data.churn_by_payment);
}

function resetDashboard() {
  showConfirm({
    title: 'Reset semua data prediksi?',
    description: 'Seluruh data prediksi akan dihapus dari sistem. Tindakan ini tidak bisa dibatalkan.',
    confirmLabel: 'Ya, reset',
    onConfirm: async () => {
      const res = await fetch('/api/insight/clear', { method: 'DELETE' });
      if (res.ok) {
        loadSummary();
        loadCharts();
        showToast('Data berhasil direset', 'success');
      } else {
        showToast('Gagal mereset data', 'error');
      }
    }
  });
}

function applyFilters() {
  const params = _getFilterParams();
  loadCharts(params);
  loadSummary(params);
}

function resetFilters() {
  ['filterGender','filterCityTier','filterMarital','filterTenureMin','filterTenureMax']
    .forEach(id => { const el = document.getElementById(id); if (el) el.value = ''; });
  loadCharts();
  loadSummary();
}

document.addEventListener('DOMContentLoaded', () => {
  loadSummary();
  loadCharts();
});
