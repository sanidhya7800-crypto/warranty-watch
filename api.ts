import axios from 'axios';
import { Product, ServiceRequest, RecallAlert, NotificationItem, TinyFishActivity, MonitorItem, DashboardMetrics, KeyStatus, TinyFishHealth } from './types';

const api = axios.create({
  baseURL: '/api',
  timeout: 120000, // 2-minute safety timeout for autonomous multi-step agent runs
});

export const getHealth = () => api.get<{ status: string; service: string }>('/health');
export const getTinyFishHealth = () => api.get<TinyFishHealth>('/tinyfish/health');

export const getDashboard = () => api.get<DashboardMetrics>('/dashboard');

export const getProducts = () => api.get<Product[]>('/products');
export const getProduct = (id: number) => api.get<Product>(`/products/${id}`);
export const createProduct = (data: Partial<Product>) => api.post<Product>('/products', data);
export const updateProduct = (id: number, data: Partial<Product>) => api.put<Product>(`/products/${id}`, data);
export const deleteProduct = (id: number) => api.delete<{ message: string }>(`/products/${id}`);
export const getCategories = () => api.get<string[]>('/products/categories');
export const getStatuses = () => api.get<string[]>('/products/statuses');

export const uploadInvoice = (productId: number, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post<Product>(`/products/${productId}/invoice`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};
export const deleteInvoice = (productId: number) => api.delete<Product>(`/products/${productId}/invoice`);
export const getInvoiceDownloadUrl = (productId: number) => `/api/products/${productId}/invoice`;

// Warranty Intelligence (Search + Fetch)
export const investigateWarranty = (payload: {
  product_id: number;
  manufacturer: string;
  model_number?: string;
  category?: string;
}) => api.post('/warranty/investigate', payload);

// AI Assistant (Search + Fetch + Agent)
export const investigateIssue = (payload: {
  product_id: number;
  issue: string;
}) => api.post('/assistant/investigate', payload);

// Service Requests
export const getServiceRequests = () => api.get<ServiceRequest[]>('/service-requests');
export const createServiceRequest = (data: Partial<ServiceRequest>) => api.post<ServiceRequest>('/service-requests', data);
export const updateServiceRequest = (id: number, data: Partial<ServiceRequest>) => api.put<ServiceRequest>(`/service-requests/${id}`, data);
export const deleteServiceRequest = (id: number) => api.delete<{ message: string }>(`/service-requests/${id}`);
export const checkServiceStatusBrowser = (id: number) => api.post(`/service-requests/${id}/check-status`);

// Recalls & Alerts
export const getRecalls = () => api.get<RecallAlert[]>('/recalls');
export const createRecall = (data: Partial<RecallAlert>) => api.post<RecallAlert>('/recalls', data);
export const deleteRecall = (id: number) => api.delete<{ message: string }>(`/recalls/${id}`);
export const discoverRecalls = (payload: { manufacturer: string; model_number?: string }) =>
  api.post('/recalls/discover', payload);

// Notifications
export const getNotifications = () => api.get<NotificationItem[]>('/notifications');
export const markNotificationRead = (id: number) => api.post<NotificationItem>(`/notifications/${id}/read`);
export const markAllNotificationsRead = () => api.post<{ message: string }>('/notifications/read-all');
export const regenerateNotifications = () => api.post<{ message: string }>('/notifications/regenerate');

// TinyFish Activity & Settings
export const getActivity = (limit = 100) => api.get<TinyFishActivity[]>(`/activity?limit=${limit}`);
export const getSettings = () => api.get<KeyStatus>('/settings');
export const updateMode = (mode: 'live' | 'demo') => api.put<{ mode: string }>('/settings/mode', { mode });

// Monitors
export const getMonitors = () => api.get<MonitorItem[]>('/monitors');
export const createMonitor = (payload: {
  name: string;
  monitor_type: 'search' | 'fetch';
  target: string;
  schedule_cron: string;
  purpose?: string;
  product_id?: number;
}) => api.post('/monitors', payload);
export const runMonitor = (id: number) => api.post(`/monitors/${id}/run`);
export const cancelMonitor = (id: number) => api.delete<{ message: string }>(`/monitors/${id}`);

export default api;
