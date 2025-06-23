// frontend/src/components/AlertPanel.jsx
import React, { useState, useEffect } from 'react';
import { getAlerts } from '../services/api';

const AlertPanel = () => {
    const [alerts, setAlerts] = useState([]);
    const [error, setError] = useState(null);

    const fetchAlerts = async (retryCount = 3, delay = 2000) => {
        for (let i = 0; i < retryCount; i++) {
            try {
                const data = await getAlerts();
                setAlerts(data);
                setError(null);
                return;
            } catch (err) {
                console.error('Error fetching alerts:', err);
                if (i < retryCount - 1) {
                    await new Promise(resolve => setTimeout(resolve, delay));
                    continue;
                }
                setError('Failed to fetch alerts. Retrying may help.');
            }
        }
    };

    useEffect(() => {
        fetchAlerts();
        const interval = setInterval(() => fetchAlerts(), 5000); // Poll every 5 seconds
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="alert-panel">
            <h2>Alerts</h2>
            {error && <p className="error">{error}</p>}
            <table>
                <thead>
                    <tr>
                        <th>Room</th>
                        <th>Description</th>
                        <th>Severity</th>
                        <th>Timestamp</th>
                    </tr>
                </thead>
                <tbody>
                    {alerts.map((alert, index) => (
                        <tr key={index}>
                            <td>{alert.room}</td>
                            <td>{alert.description}</td>
                            <td>{alert.severity}</td>
                            <td>{new Date(alert.timestamp * 1000).toLocaleString()}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default AlertPanel;