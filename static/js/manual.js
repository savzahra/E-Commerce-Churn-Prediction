// Manual Input Handler
let gaugeChart = null;

async function runManualPrediction(event) {
  event.preventDefault();
  const form = event.target;
  const formData = new FormData(form);

  // Build payload with correct types
  const payload = {
    Tenure: parseFloat(formData.get('Tenure')),
    PreferredLoginDevice: formData.get('PreferredLoginDevice'),
    CityTier: parseInt(formData.get('CityTier')),
    WarehouseToHome: parseFloat(formData.get('WarehouseToHome')),
    PreferredPaymentMode: formData.get('PreferredPaymentMode'),
    Gender: formData.get('Gender'),
    HourSpendOnApp: parseFloat(formData.get('HourSpendOnApp')),
    NumberOfDeviceRegistered: parseInt(formData.get('NumberOfDeviceRegistered')),
    PreferedOrderCat: formData.get('PreferedOrderCat'),
    SatisfactionScore: parseInt(formData.get('SatisfactionScore')),
    MaritalStatus: formData.get('MaritalStatus'),
    NumberOfAddress: parseInt(formData.get('NumberOfAddress')),
    Complain: parseInt(formData.get('Complain')),
    OrderAmountHikeFromlastYear: parseFloat(formData.get('OrderAmountHikeFromlastYear')),
    CouponUsed: parseFloat(formData.get('CouponUsed')),
    OrderCount: parseFloat(formData.get('OrderCount')),
    DaySinceLastOrder: parseFloat(formData.get('DaySinceLastOrder')),
    CashbackAmount: parseFloat(formData.get('CashbackAmount')),
  };

  showLoading();
  try {
    const res = await fetch('/api/predict/manual', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) {
      showToast(data.detail || 'Gagal melakukan prediksi', 'error');
      return;
    }
    renderManualResult(data.prediction, payload);
    showToast('Prediksi berhasil!', 'success');
  } catch (err) {
    showToast('Network error: ' + err.message, 'error');
  } finally {
    hideLoading();
  }
}

function renderManualResult(pred, input) {
  const { churn_label, churn_probability, risk_level } = pred;
  const pct = (churn_probability * 100).toFixed(1);

  // Show result card
  document.getElementById('manualResultCard').style.display = 'block';
  document.getElementById('manualPlaceholder').style.display = 'none';

  // Gauge
  const gaugeColor = risk_level === 'High' ? '#ef4444' : risk_level === 'Medium' ? '#f59e0b' : '#10b981';
  renderGauge(churn_probability, gaugeColor);

  document.getElementById('gaugePct').textContent = pct + '%';
  document.getElementById('gaugePct').style.color = gaugeColor;

  // Risk badge
  document.getElementById('manualRiskBadge').innerHTML =
    `<span class="risk-badge ${risk_level}" style="font-size:14px;padding:6px 16px">● ${risk_level} Risk</span>`;

  // Churn label
  const isChurn = churn_label === 1;
  document.getElementById('manualChurnLabel').textContent = isChurn ? '⚠️ Berpotensi Churn' : '✅ Tidak Churn';
  document.getElementById('manualChurnLabel').style.color = isChurn ? '#f87171' : '#34d399';
  document.getElementById('manualProb').textContent = `Probabilitas churn: ${pct}%`;

  // Insight
  document.getElementById('manualInsight').querySelector('p').innerHTML = generateInsight(pred, input);
}

function renderGauge(value, color) {
  const ctx = document.getElementById('gaugeChart').getContext('2d');
  if (gaugeChart) { gaugeChart.destroy(); gaugeChart = null; }

  const remaining = 1 - value;
  gaugeChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [value, remaining],
        backgroundColor: [color, 'rgba(255,255,255,0.06)'],
        borderColor: [color, 'transparent'],
        borderWidth: 2,
        hoverOffset: 0,
      }]
    },
    options: {
      cutout: '72%',
      rotation: -90,
      circumference: 180,
      responsive: false,
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { duration: 800, easing: 'easeOutQuart' },
    }
  });
}

function generateInsight(pred, input) {
  const lines = [];
  const { risk_level } = pred;

  if (input.Tenure <= 6) {
    lines.push('🔴 Pelanggan baru (<6 bulan) — risiko churn tertinggi, perlu program onboarding intensif.');
  } else if (input.Tenure >= 24) {
    lines.push('🟢 Tenure panjang (24+ bulan) — loyalitas tinggi, risiko churn sangat rendah.');
  }

  if (input.Complain === 1) {
    lines.push('⚠️ Pernah komplain — perlu tindak lanjut cepat untuk mencegah churn.');
  }

  if (input.SatisfactionScore <= 2) {
    lines.push('😞 Satisfaction score rendah — segera berikan insentif retensi.');
  } else if (input.SatisfactionScore >= 4) {
    lines.push('😊 Satisfaction tinggi — pelanggan puas, pertahankan kualitas layanan.');
  }

  if (input.MaritalStatus === 'Single') {
    lines.push('📊 Status Single — kelompok dengan churn rate tertinggi (26.7%).');
  }

  if (input.PreferedOrderCat === 'Mobile Phone') {
    lines.push('📱 Kategori Mobile Phone — churn rate kategori ini ~27%, perlu perhatian khusus.');
  }

  if (lines.length === 0) {
    lines.push(risk_level === 'Low'
      ? '✅ Profil pelanggan menunjukkan risiko rendah. Pertahankan engagement.'
      : '📋 Monitor secara berkala dan berikan program loyalitas yang sesuai.');
  }

  return lines.join('<br>');
}

function clearManualResult() {
  document.getElementById('manualResultCard').style.display = 'none';
  document.getElementById('manualPlaceholder').style.display = 'block';
}

function fillSampleData() {
  const form = document.getElementById('manualForm');
  const samples = [
    { Tenure: 2, PreferredLoginDevice: 'Mobile Phone', CityTier: 1, WarehouseToHome: 30,
      PreferredPaymentMode: 'Credit Card', Gender: 'Female', HourSpendOnApp: 2,
      NumberOfDeviceRegistered: 2, PreferedOrderCat: 'Mobile Phone', SatisfactionScore: 2,
      MaritalStatus: 'Single', NumberOfAddress: 2, Complain: 1, OrderAmountHikeFromlastYear: 10,
      CouponUsed: 1, OrderCount: 2, DaySinceLastOrder: 10, CashbackAmount: 150 },
    { Tenure: 30, PreferredLoginDevice: 'Computer', CityTier: 2, WarehouseToHome: 12,
      PreferredPaymentMode: 'Debit Card', Gender: 'Male', HourSpendOnApp: 4,
      NumberOfDeviceRegistered: 4, PreferedOrderCat: 'Laptop & Accessory', SatisfactionScore: 5,
      MaritalStatus: 'Married', NumberOfAddress: 4, Complain: 0, OrderAmountHikeFromlastYear: 20,
      CouponUsed: 3, OrderCount: 5, DaySinceLastOrder: 2, CashbackAmount: 250 },
  ];
  const sample = samples[Math.floor(Math.random() * samples.length)];

  Object.entries(sample).forEach(([key, val]) => {
    const el = form.querySelector(`[name="${key}"]`);
    if (el) el.value = val;
  });

  showToast('Contoh data berhasil diisi', 'info');
}
