import axios from 'axios';

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000',
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export const login = (email, password) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  return apiClient.post('/login/', formData);
};

export const register = (userData) => {
  return apiClient.post('/register/', userData);
};

export const uploadDocument = (formData) => {
  return apiClient.post('/documents/upload/', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const searchDocuments = (query, tag) => {
  return apiClient.get(`/documents/search/?q=${query}&tag=${tag}`);
};

export const getDocumentVersions = (docId) => {
  return apiClient.get(`/documents/${docId}/versions/`);
};

export const getDepartments = () => {
  return apiClient.get('/departments/');
};

export const downloadDocument = async (docId, filename) => {
  const response = await apiClient.get(`/documents/${docId}/download/`, {
    responseType: 'blob', 
  });
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
};