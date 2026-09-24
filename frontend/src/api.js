import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  timeout: 20000,
});

export const getHealth = () => api.get("/health");
export const getRoot = () => api.get("/");
export const predict = (payload) => api.post("/predict", payload);
export const getIoTStatus = () => api.get("/iot/status");
export const getDevices = () => api.get("/iot/devices");
export const pushToDevice = (payload) => api.post("/iot/push", payload);
export const getPredictions = (limit = 50) => api.get("/predictions", { params: { limit } });
export const getAnalytics = () => api.get("/analytics");
export const getModelInfo = () => api.get("/model-info");
export const getSettings = () => api.get("/settings");

export default api;
