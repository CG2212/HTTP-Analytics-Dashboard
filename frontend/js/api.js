let requestsChart = null;

// 1. Render Date-Wise Request Line Chart
function renderRequestsChart(sessions) {
    if (!sessions || !Array.isArray(sessions)) return;

    // Group requests by Date and collect valid Date objects for sorting
    const dateMap = {};

    sessions.forEach(session => {
        let dateKey = 'Recent';
        let sortVal = 0;
        const dateHeader = session.response && session.response.headers && session.response.headers.date;
        
        if (dateHeader) {
            try {
                const parsedDate = new Date(dateHeader);
                if (!isNaN(parsedDate)) {
                    sortVal = parsedDate.getTime();
                    dateKey = parsedDate.toLocaleDateString('en-US', { 
                        month: 'short', 
                        day: 'numeric', 
                        year: 'numeric' 
                    });
                }
            } catch (e) {}
        }

        if (!dateMap[dateKey]) {
            dateMap[dateKey] = { count: 0, sortVal: sortVal };
        }
        dateMap[dateKey].count += 1;
    });

    // Sort dates chronologically (oldest to newest)
    const sortedKeys = Object.keys(dateMap).sort((a, b) => dateMap[a].sortVal - dateMap[b].sortVal);

    const labels = sortedKeys;
    const dataCounts = sortedKeys.map(label => dateMap[label].count);

    const canvasEl = document.getElementById('requestsLineChart');
    if (!canvasEl) return;
    const ctx = canvasEl.getContext('2d');

    if (requestsChart) {
        requestsChart.data.labels = labels;
        requestsChart.data.datasets[0].data = dataCounts;
        requestsChart.update();
    } else {
        requestsChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Requests per Day (Loaded Sessions)',
                    data: dataCounts,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: true }
                },
                scales: {
                    x: { grid: { display: false } },
                    y: { beginAtZero: true, ticks: { precision: 0 } }
                }
            }
        });
    }
}

// 2. Render Metric Counters and Breakdown Lists
function updateDashboardUI(data) {
    if (!data) return;

    // Update Top Metric Counters
    if (data.metrics) {
        const totalReqEl = document.getElementById('total-requests');
        const totalResEl = document.getElementById('total-responses');
        const totalAgentsEl = document.getElementById('total-agents');

        if (totalReqEl) totalReqEl.innerText = data.metrics.total_requests || 0;
        if (totalResEl) totalResEl.innerText = data.metrics.total_responses || 0;
        if (totalAgentsEl && data.metrics.user_agents) {
            totalAgentsEl.innerText = Object.keys(data.metrics.user_agents).length;
        }

        // Render Breakdown Lists
        renderStatList('methods-list', data.metrics.methods);
        renderStatList('status-list', data.metrics.status_codes);
        renderStatList('agents-list', data.metrics.user_agents);
    }

    // Render Sessions List & Date-Wise Chart
    if (data.sessions) {
        renderSessionsList(data.sessions);
        renderRequestsChart(data.sessions);
    }
}

// Helper for rendering breakdown lists
function renderStatList(containerId, obj) {
    const container = document.getElementById(containerId);
    if (!container || !obj) return;
    container.innerHTML = '';
    
    for (const [key, value] of Object.entries(obj)) {
        const item = document.createElement('div');
        item.style.display = 'flex';
        item.style.justifyContent = 'space-between';
        item.style.padding = '6px 0';
        item.style.borderBottom = '1px solid #f1f5f9';
        item.innerHTML = `<span style="font-weight: 500; color: #334155;">${key}</span> <span style="color: #64748b; font-weight: 600;">${value}</span>`;
        container.appendChild(item);
    }
}

// Helper for rendering captured session items and inspector handler
function renderSessionsList(sessions) {
    const container = document.getElementById('session-list');
    if (!container) return;
    container.innerHTML = '';
    
    sessions.forEach(session => {
        const div = document.createElement('div');
        div.style.padding = '8px 10px';
        div.style.borderBottom = '1px solid #e2e8f0';
        div.style.cursor = 'pointer';
        div.style.borderRadius = '4px';
        div.style.transition = 'background 0.2s';
        
        const method = session.request?.method || 'GET';
        const url = session.request?.url || '/';
        const status = session.response?.statuscode || 200;

        div.innerHTML = `<strong>${method}</strong> <span style="color: #475569;">${url}</span> <span style="float: right; color: #22c55e; font-weight: bold;">${status}</span>`;
        
        div.addEventListener('mouseenter', () => div.style.background = '#f8fafc');
        div.addEventListener('mouseleave', () => div.style.background = 'transparent');

        div.addEventListener('click', () => {
            const detailsContainer = document.getElementById('session-details');
            if (detailsContainer) {
                detailsContainer.innerHTML = `<pre style="font-size: 11px; background: #f8fafc; padding: 12px; border-radius: 6px; overflow-x: auto; color: #334155;">${JSON.stringify(session, null, 2)}</pre>`;
            }
        });

        container.appendChild(div);
    });
}

// 3. Fetch Data from FastAPI Backend
async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard-data');
        const data = await response.json();
        updateDashboardUI(data);
    } catch (err) {
        console.error("Error loading dashboard data:", err);
    }
}

// Initialize on DOM load and poll every 5 seconds
window.addEventListener('DOMContentLoaded', () => {
    loadDashboardData();
    setInterval(loadDashboardData, 5000);
});