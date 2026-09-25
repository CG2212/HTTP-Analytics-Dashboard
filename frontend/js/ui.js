const sessionList = document.getElementById('session-list');
const sessionDetails = document.getElementById('session-details');
const sessionsMap = new Map();

export function updateMetricsUI(metrics) {
    document.getElementById('total-requests').innerText = metrics.total_requests;
    document.getElementById('total-responses').innerText = metrics.total_responses;
    document.getElementById('total-agents').innerText = Object.keys(metrics.user_agents).length;

    renderBreakdown('methods-list', metrics.methods);
    renderBreakdown('status-list', metrics.status_codes);
    renderBreakdown('agents-list', metrics.user_agents);
}

function renderBreakdown(elementId, dataMap) {
    const container = document.getElementById(elementId);
    container.innerHTML = '';
    for (const [key, count] of Object.entries(dataMap)) {
        const item = document.createElement('div');
        item.className = 'stat-item';
        item.innerHTML = `<span>${key}</span> <strong>${count}</strong>`;
        container.appendChild(item);
    }
}

export function renderSessionItem(session, prepend = true) {
    sessionsMap.set(session.id, session);
    const div = document.createElement('div');
    div.className = 'session-item';
    div.onclick = () => showDetails(session.id);
    
    const statusCode = session.response.statusCode || '500';
    let statusClass = 'status-2xx';
    if (statusCode.toString().startsWith('4')) statusClass = 'status-4xx';
    if (statusCode.toString().startsWith('5')) statusClass = 'status-5xx';

    div.innerHTML = `
        <div>
            <span class="method ${session.request.method}">${session.request.method}</span>
            <span style="font-size: 13px; margin-left: 8px; color: #334155;">${session.request.url}</span>
        </div>
        <span class="status ${statusClass}">${statusCode}</span>
    `;
    
    if (prepend && sessionList.firstChild) {
        sessionList.insertBefore(div, sessionList.firstChild);
    } else {
        sessionList.appendChild(div);
    }
}

export function showDetails(id) {
    const session = sessionsMap.get(id);
    if (!session) return;

    sessionDetails.innerHTML = `
        <h4 style="color: #0284c7; margin-bottom: 5px;">Request Headers (${session.request.method} ${session.request.url})</h4>
        <pre>${JSON.stringify(session.request.headers, null, 2)}</pre>
        
        <h4 style="color: #0284c7; margin-bottom: 5px;">Response Headers (Status: ${session.response.statusCode})</h4>
        <pre>${JSON.stringify(session.response.headers, null, 2)}</pre>
    `;
}