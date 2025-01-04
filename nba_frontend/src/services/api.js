import axios from 'axios';

// Define the base URL for the API
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Create axios instance with default config
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    }
});

// Add response interceptor for debugging
api.interceptors.response.use(
    response => {
        console.log('API Response:', response);
        return response;
    },
    error => {
        console.error('API Error:', error.response || error);
        return Promise.reject(error);
    }
);

// API endpoints
export const fetchNBAData = async () => {
    try {
        const { data } = await api.get('/data/');  // Adjust this to match your Django URL
        
        // Log the received data for debugging
        console.log('Received NBA data:', data);
        
        return data;
    } catch (error) {
        console.error('Error fetching NBA data:', error);
        throw error;
    }
};

export const fetchSeasons = async () => {
    try {
        const { data } = await api.get('/seasons/');
        return data;
    } catch (error) {
        console.error('Error fetching seasons:', error);
        throw error;
    }
};

export const fetchSeasonStats = async (seasonId) => {
    try {
        const { data } = await api.get(`/seasons/${seasonId}/`);
        return data;
    } catch (error) {
        console.error('Error fetching season stats:', error);
        throw error;
    }
};

export default api;