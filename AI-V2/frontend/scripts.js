const form = document.getElementById('lead-form');
const resultsSection = document.getElementById('results');
const leadBody = document.getElementById('lead-body');
const logList = document.getElementById('log-list');

let currentJobId = null;
let logInterval = null;

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const prompt = document.getElementById('prompt').value.trim();
  const targetCount = parseInt(document.getElementById('target').value, 10);

  const response = await fetch('/leads/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt, target_count: targetCount })
  });
  const data = await response.json();
  currentJobId = data.job_id;
  renderLeads(data.leads);
  resultsSection.hidden = false;
  startLogPolling();
});

function renderLeads(leads) {
  leadBody.innerHTML = '';
  leads.forEach(lead => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${lead.contact_name}</td>
      <td>${lead.title ?? ''}</td>
      <td>${lead.company ?? ''}</td>
      <td>${lead.email ? `<a href="mailto:${lead.email}">${lead.email}</a>` : ''}</td>
      <td>${lead.linkedin ? `<a href="${lead.linkedin}" target="_blank">Profile</a>` : ''}</td>
      <td>${Math.round((lead.confidence ?? 0) * 100)}%</td>
    `;
    leadBody.appendChild(row);
  });
}

async function startLogPolling() {
  if (logInterval) clearInterval(logInterval);
  logInterval = setInterval(async () => {
    if (!currentJobId) return;
    const resp = await fetch(`/logs/${currentJobId}`);
    const logs = await resp.json();
    logList.innerHTML = '';
    logs.forEach(log => {
      const item = document.createElement('li');
      item.textContent = `[${log.created_at}] ${log.level}: ${log.message}`;
      logList.appendChild(item);
    });
  }, 3000);
}
