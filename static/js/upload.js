// CSV Upload Handler
let uploadedFile = null;
let csvSessionId = null;

// Drag & drop
const uploadZone = document.getElementById('uploadZone');
if (uploadZone) {
  uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
  uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
  uploadZone.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file) processFile(file);
  });
}

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) processFile(file);
}

function processFile(file) {
  if (!file.name.endsWith('.csv')) {
    showToast('Hanya file CSV yang didukung', 'error');
    return;
  }
  uploadedFile = file;
  document.getElementById('fileName').textContent = file.name;
  document.getElementById('fileRows').textContent = `(${(file.size / 1024).toFixed(1)} KB)`;
  document.getElementById('fileInfo').style.display = 'block';
  document.getElementById('uploadTitle').textContent = 'File berhasil dipilih';
  document.getElementById('uploadSubtitle').textContent = 'Klik "Jalankan Prediksi" untuk memulai';
  document.getElementById('btnPredict').disabled = false;
  document.getElementById('csvStatus').textContent = '';
}

function clearFile() {
  uploadedFile = null;
  document.getElementById('csvFile').value = '';
  document.getElementById('fileInfo').style.display = 'none';
  document.getElementById('uploadTitle').textContent = 'Drag & drop atau klik untuk upload';
  document.getElementById('uploadSubtitle').textContent = 'Format: CSV dengan 18 kolom. Maks 10MB.';
  document.getElementById('btnPredict').disabled = true;
  document.getElementById('csvStatus').textContent = '';
  document.getElementById('csvResultSection').style.display = 'none';
}

async function runCsvPrediction() {
  if (!uploadedFile) { showToast('Pilih file CSV terlebih dahulu', 'error'); return; }

  const formData = new FormData();
  formData.append('file', uploadedFile);

  showLoading();
  const statusEl = document.getElementById('csvStatus');
  statusEl.textContent = 'Memproses...';

  try {
    const res = await fetch('/api/predict/csv', { method: 'POST', body: formData });
    const data = await res.json();

    if (!res.ok) {
      // Structured error for missing columns
      if (data.detail && typeof data.detail === 'object' && data.detail.missing) {
        const missing = data.detail.missing;
        showToast(`${missing.length} kolom tidak ditemukan — lihat detail di bawah`, 'error', 6000);
        statusEl.innerHTML = `<span style="color:var(--high)">Kolom tidak ditemukan: <strong>${missing.join(', ')}</strong></span>`;
      } else {
        showToast(typeof data.detail === 'string' ? data.detail : 'Gagal memproses CSV', 'error');
        statusEl.textContent = '';
      }
      return;
    }

    csvSessionId = data.session_id;
    // Only store session_id — full results stay server-side to avoid sessionStorage quota
    sessionStorage.setItem('churnSessionId', csvSessionId);

    renderCsvResults(data.results);
    showToast(`✅ ${data.total} baris berhasil diprediksi`, 'success');
    statusEl.textContent = `${data.total} baris diproses`;
  } catch (err) {
    showToast('Network error: ' + err.message, 'error');
  } finally {
    hideLoading();
  }
}

function renderCsvResults(results) {
  const section = document.getElementById('csvResultSection');
  section.style.display = 'block';

  const total  = results.length;
  const churn  = results.filter(r => r.churn_label === 1).length;
  const medium = results.filter(r => r.risk_level === 'Medium').length;
  const high   = results.filter(r => r.risk_level === 'High').length;

  document.getElementById('qsTotal').textContent  = total;
  document.getElementById('qsChurn').textContent  = churn;
  document.getElementById('qsMedium').textContent = medium;
  document.getElementById('qsHigh').textContent   = high;

  // Show CustomerID column header only if data has it
  const hasId = results.length > 0 && 'CustomerID' in results[0];
  const colHeader = document.getElementById('colCustId');
  if (colHeader) colHeader.style.display = hasId ? '' : 'none';

  // Preview first 10 rows
  const preview = results.slice(0, 10);
  const tbody = document.getElementById('previewBody');
  tbody.innerHTML = preview.map(r => {
    const pct = (r.churn_probability * 100).toFixed(1);
    const barColor = r.risk_level === 'High' ? '#f87171' : r.risk_level === 'Medium' ? '#f59e0b' : '#10b981';
    const cidCell = hasId
      ? `<td style="font-family:monospace;font-size:12px;color:var(--accent-text)">${r.CustomerID ?? '—'}</td>`
      : '';
    return `<tr>
      <td class="text-muted text-xs">${r.row_index}</td>
      ${cidCell}
      <td>${r.Tenure ?? '—'}</td>
      <td>${r.Gender ?? '—'}</td>
      <td>${r.MaritalStatus ?? '—'}</td>
      <td>${r.CityTier ?? '—'}</td>
      <td>
        <div class="prob-bar-wrapper">
          <div class="prob-bar-bg"><div class="prob-bar-fill" style="width:${pct}%;background:${barColor}"></div></div>
          <span class="prob-value">${pct}%</span>
        </div>
      </td>
      <td><span class="risk-badge ${r.risk_level}">${r.risk_level}</span></td>
      <td><span class="label-badge ${r.churn_label===1?'churn':'no-churn'}">${r.churn_label===1?'Churn':'Aman'}</span></td>
    </tr>`;
  }).join('');

  const note = document.getElementById('previewNote');
  note.textContent = total > 10 ? `Menampilkan 10 dari ${total} baris — lihat semua di halaman Result.` : '';

  section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function downloadResult() {
  if (!csvSessionId) { showToast('Tidak ada data untuk didownload', 'error'); return; }
  window.location.href = `/api/predict/download/${csvSessionId}`;
}

function switchTab(tab) {
  document.getElementById('tabCsv').style.display = tab === 'csv' ? 'block' : 'none';
  document.getElementById('tabManual').style.display = tab === 'manual' ? 'block' : 'none';
  document.getElementById('tabCsvBtn').classList.toggle('active', tab === 'csv');
  document.getElementById('tabManualBtn').classList.toggle('active', tab === 'manual');
}
