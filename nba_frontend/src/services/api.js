import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL
});

export const fetchNBAData = async () => {
  const { data } = await api.get('/data/');
  return data;
};

export const fetchSeasons = async () => {
  const { data } = await api.get('/seasons/');
  return data;
};

export const fetchSeasonStats = async (seasonId) => {
  const { data } = await api.get(`/stats/${seasonId}/`);
  return data;
};

export const fetchTeams = async () => {
  const { data } = await api.get('/teams/');
  return data;
};

export default api;