import axios from 'axios';

const API_URL = 'http://localhost:5000';

export const getPlayers = async () => {
  const response = await axios.get(`${API_URL}/players`);
  return response.data;
};

export const getPlayer = async (id) => {
  const response = await axios.get(`${API_URL}/players/${id}`);
  return response.data;
};

export const getVisualizationData = async () => {
  const response = await axios.get(`${API_URL}/visualization`);
  return response.data;
};

export const triggerScrape = async () => {
  const response = await axios.post(`${API_URL}/scrape`);
  return response.data;
};
