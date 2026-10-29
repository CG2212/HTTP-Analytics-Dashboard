let incidentsCache = [];

async function loadIncidentsQueue() {
    try {
        const response = await fetch('/api/incidents/');
        const data = await response.json();
        
        incidentsCache = Array.isArray(data) ? data : (data.queue || []);

        let totalOccurrences = 0;
        let activeCount = 0;

        const tbody = document.getElementById('incidents-table-body');
        
        if (!incidentsCache || incidentsCache.length === 0) {
            tbody.innerHTML = `<tr><td colspan="6" style="padding: 16px; text-align: center; color: #16a34a;">No error telemetry logged. System is fully operational! ✨</td></tr>`;
            document.getElementById('stat-total-errors').textContent = '0';
            document.getElementById('stat-total-occurrences').textContent = '0';
            document.getElementById('stat-system-status').textContent = 'Healthy';
            document.getElementById('stat-system-status').style.color = '#16a34a';
            return;
        }

        tbody.innerHTML = incidentsCache.map((inc, index) => {
            totalOccurrences += (inc.occurrences || 1);
            
            // Normalize status check to lowercase to catch "unresolved", "active", "investigating"
            const statusLower = (inc.status || '').toLowerCase();
            if (statusLower === 'active' || statusLower === 'investigating' || statusLower === 'unresolved') {
                activeCount++;
            }

            const isResolved = statusLower === 'resolved';
            const statusColor = isResolved ? '#16a34a' : '#dc2626';
            const statusBg = isResolved ? '#dcfce7' : '#fee2e2';

            return `
                <tr style="border-bottom: 1px solid #e2e8f0; cursor: pointer; transition: background 0.2s;" onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'" onclick="inspectStackTrace(${index})">
                    <td style="padding: 12px; max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="${inc.error_message}">
                        <strong>${inc.error_fingerprint}</strong><br>
                        <small style="color: #64748b;">${inc.error_message}</small>
                    </td>
                    <td style="padding: 12px;">
                        <span style="background: ${statusBg}; color: ${statusColor}; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; text-transform: uppercase;">
                            ${inc.status}
                        </span>
                    </td>
                    <td style="padding: 12px; font-weight: bold; color: #334155;">${inc.occurrences || 1}</td>
                    <td style="padding: 12px; font-size: 12px; color: #64748b;">${inc.first_seen ? new Date(inc.first_seen).toLocaleString() : 'N/A'}</td>
                    <td style="padding: 12px; font-size: 12px; color: #64748b;">${inc.last_seen ? new Date(inc.last_seen).toLocaleString() : 'N/A'}</td>
                    <td style="padding: 12px;">
                        <button onclick="event.stopPropagation(); inspectStackTrace(${index})" style="background: #e2e8f0; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 12px;">Inspect</button>
                    </td>
                </tr>
            `;
        }).join('');

        document.getElementById('stat-total-errors').textContent = incidentsCache.length;
        document.getElementById('stat-total-occurrences').textContent = totalOccurrences;
        
        const statusEl = document.getElementById('stat-system-status');
        if (activeCount > 0) {
            statusEl.textContent = `${activeCount} Unresolved`;
            statusEl.style.color = '#dc2626';
        } else {
            statusEl.textContent = 'All Resolved';
            statusEl.style.color = '#16a34a';
        }

    } catch (err) {
        console.error("Failed to load incidents queue:", err);
        document.getElementById('incidents-table-body').innerHTML = `<tr><td colspan="6" style="padding: 16px; text-align: center; color: #dc2626;">Error loading telemetry endpoint.</td></tr>`;
    }
}

function inspectStackTrace(index) {
    const item = incidentsCache[index];
    const viewer = document.getElementById('stack-trace-viewer');
    if (item && item.stack_trace) {
        viewer.textContent = item.stack_trace;
    } else {
        viewer.textContent = "No stack trace recorded for this fingerprint.";
    }
}

window.loadIncidentsQueue = loadIncidentsQueue;
window.inspectStackTrace = inspectStackTrace;

window.addEventListener('DOMContentLoaded', () => {
    loadIncidentsQueue();
    setInterval(loadIncidentsQueue, 5000);
});