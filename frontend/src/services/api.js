// frontend/src/services/api.js
import axios from 'axios';

const api = axios.create({
    baseURL: 'http://localhost:5000',
    timeout: 5000,
});

export const getAlerts = async () => {
    try {
        const response = await api.get('/api/alerts');
        return response.data.alerts;
    } catch (error) {
        console.error('Error fetching alerts:', error);
        throw error;
    }
};