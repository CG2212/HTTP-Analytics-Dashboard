import { updateMetricsUI, renderSessionItem } from './ui.js';

export function initializeApp() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${wsProtocol}//${window.location.host}/ws`);

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.metrics) updateMetricsUI(data.metrics);
        if (data.session) renderSessionItem(data.session, true);
    };

    fetch('/api/dashboard-data')
        .then(res => res.json())
        .then(data => {
            updateMetricsUI(data.metrics);
            data.sessions.forEach(session => renderSessionItem(session, false));
        });
}

document.addEventListener('DOMContentLoaded', initializeApp);