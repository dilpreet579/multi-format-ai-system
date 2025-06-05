document.getElementById('uploadForm').onsubmit = async function(e) {
  e.preventDefault();
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true;
  const formData = new FormData();
  const file = document.getElementById('fileInput').files[0];
  const json = document.getElementById('jsonInput').value;
  if (file) formData.append('file', file);
  if (json) formData.append('json_data', json);
  setResult('<div class="spinner-border text-primary" role="status" aria-live="polite"><span class="visually-hidden">Loading...</span></div> <em>Processing...</em>');
  clearLogs();
  try {
    const res = await fetch('/upload', { method: 'POST', body: formData });
    const data = await res.json();
    setResult(renderResultSummary(data) + '<pre>' + syntaxHighlight(data) + '</pre>');
    document.getElementById('uploadForm').reset();
  } catch (err) {
    setResult('<div class="alert alert-danger" role="alert" aria-live="assertive">Error: ' + err + '</div>');
  }
  submitBtn.disabled = false;
};

async function fetchLogs() {
  setLogs('<div class="spinner-border text-secondary" role="status" aria-live="polite"><span class="visually-hidden">Loading...</span></div> <em>Loading logs...</em>');
  try {
    const res = await fetch('/logs');
    const data = await res.json();
    setLogs('<pre>' + syntaxHighlight(data) + '</pre>');
    // Expand logs panel if collapsed
    const logsPanel = document.getElementById('logsPanel');
    if (logsPanel && !logsPanel.classList.contains('show')) {
      new bootstrap.Collapse(logsPanel, {toggle: true});
    }
  } catch (err) {
    setLogs('<div class="alert alert-danger" role="alert" aria-live="assertive">Error: ' + err + '</div>');
  }
}

function setResult(html) {
  document.getElementById('result').innerHTML = html;
}
function setLogs(html) {
  document.getElementById('logs').innerHTML = html;
}
function clearLogs() {
  document.getElementById('logs').innerHTML = '';
}

// Syntax highlight JSON
function syntaxHighlight(json) {
  if (typeof json != 'string') {
    json = JSON.stringify(json, undefined, 2);
  }
  json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
    let cls = 'number';
    if (/^"/.test(match)) {
      if (/:$/.test(match)) {
        cls = 'key';
      } else {
        cls = 'string';
      }
    } else if (/true|false/.test(match)) {
      cls = 'boolean';
    } else if (/null/.test(match)) {
      cls = 'null';
    }
    return '<span class="json-' + cls + '">' + match + '</span>';
  });
}

// Render a summary card for the result
function renderResultSummary(data) {
  if (!data || !data.classification || !data.action) return '';
  const { classification, action } = data;
  const fmt = classification.format || '-';
  const intent = classification.intent || '-';
  const actionBox = action.type || '-';
  return `
    <div class="card mb-3 border-primary" style="max-width: 100%;">
      <div class="card-body p-3">
        <div class="row g-2 align-items-center">
          <div class="col-md-4 col-6"><span class="fw-bold">Format:</span> <span class="badge bg-primary">${fmt}</span></div>
          <div class="col-md-4 col-6"><span class="fw-bold">Intent:</span> <span class="badge bg-success">${intent}</span></div>
          <div class="col-md-4 col-6"><span class="fw-bold">Action:</span> <span class="badge bg-warning text-dark">${actionBox}</span></div>
        </div>
      </div>
    </div>
  `;
} 