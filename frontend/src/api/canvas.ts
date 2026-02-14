import { apiClient } from './client';

// Types
export interface VBU {
  id: string;
  name: string;
  gm_id: string;
  gm_name: string;
  created_at: string;
  updated_at: string;
  updated_by?: string;
}

export interface Canvas {
  id: string;
  vbu_id: string;
  product_name?: string;
  lifecycle_lane: 'build' | 'sell' | 'milk' | 'reframe';
  success_description?: string;
  future_state_intent?: string;
  primary_focus?: string;
  resist_doing?: string;
  good_discipline?: string;
  primary_constraint?: string;
  currently_testing_type?: 'thesis' | 'proof_point';
  currently_testing_id?: string;
  portfolio_notes?: string;
  theses: Thesis[];
  created_at: string;
  updated_at: string;
  updated_by?: string;
}

export interface Thesis {
  id: string;
  order: number;
  text: string;
  proof_points: ProofPoint[];
  created_at: string;
  updated_at: string;
}

export interface ProofPoint {
  id: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'observed' | 'stalled';
  evidence_note?: string;
  target_review_month?: string;
  attachments: Attachment[];
  created_at: string;
  updated_at: string;
}

export interface Attachment {
  id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  label?: string;
  uploaded_by: string;
  created_at: string;
}

export interface ApiResponse<T> {
  data: T;
  meta: {
    timestamp: string;
    total?: number;
    page?: number;
    per_page?: number;
  };
}

// VBU Operations
export const listVbus = async (params?: { page?: number; per_page?: number; gm_id?: string; name?: string }): Promise<VBU[]> => {
  const response = await apiClient.get<ApiResponse<VBU[]>>('/vbus', { params });
  return response.data.data;
};

export const getVbu = async (id: string): Promise<VBU> => {
  const response = await apiClient.get<ApiResponse<VBU>>(`/vbus/${id}`);
  return response.data.data;
};

export const createVbu = async (data: { name: string; gm_id: string }): Promise<VBU> => {
  const response = await apiClient.post<ApiResponse<VBU>>('/vbus', data);
  return response.data.data;
};

export const updateVbu = async (id: string, data: { name?: string; gm_id?: string }): Promise<VBU> => {
  const response = await apiClient.patch<ApiResponse<VBU>>(`/vbus/${id}`, data);
  return response.data.data;
};

export const deleteVbu = async (id: string): Promise<void> => {
  await apiClient.delete(`/vbus/${id}`);
};

// Canvas Operations
export const getCanvas = async (vbuId: string): Promise<Canvas> => {
  const response = await apiClient.get<ApiResponse<Canvas>>(`/vbus/${vbuId}/canvas`);
  return response.data.data;
};

export const updateCanvas = async (vbuId: string, data: Partial<Canvas>): Promise<Canvas> => {
  const response = await apiClient.put<ApiResponse<Canvas>>(`/vbus/${vbuId}/canvas`, data);
  return response.data.data;
};

// Thesis Operations
export const listTheses = async (canvasId: string): Promise<Thesis[]> => {
  const response = await apiClient.get<ApiResponse<Thesis[]>>(`/canvases/${canvasId}/theses`);
  return response.data.data;
};

export const createThesis = async (canvasId: string, data: { text: string; order: number }): Promise<Thesis> => {
  const response = await apiClient.post<ApiResponse<Thesis>>(`/canvases/${canvasId}/theses`, data);
  return response.data.data;
};

export const updateThesis = async (id: string, data: { text: string }): Promise<Thesis> => {
  const response = await apiClient.patch<ApiResponse<Thesis>>(`/theses/${id}`, data);
  return response.data.data;
};

export const deleteThesis = async (id: string): Promise<void> => {
  await apiClient.delete(`/theses/${id}`);
};

export const reorderTheses = async (canvasId: string, thesisOrders: Array<{ id: string; order: number }>): Promise<Thesis[]> => {
  const response = await apiClient.put<ApiResponse<Thesis[]>>(`/canvases/${canvasId}/theses/reorder`, {
    thesis_orders: thesisOrders
  });
  return response.data.data;
};

// ProofPoint Operations
export const listProofPoints = async (thesisId: string): Promise<ProofPoint[]> => {
  const response = await apiClient.get<ApiResponse<ProofPoint[]>>(`/theses/${thesisId}/proof-points`);
  return response.data.data;
};

export const createProofPoint = async (thesisId: string, data: {
  description: string;
  status?: 'not_started' | 'in_progress' | 'observed' | 'stalled';
  evidence_note?: string;
  target_review_month?: string;
}): Promise<ProofPoint> => {
  const response = await apiClient.post<ApiResponse<ProofPoint>>(`/theses/${thesisId}/proof-points`, data);
  return response.data.data;
};

export const updateProofPoint = async (id: string, data: {
  description?: string;
  status?: 'not_started' | 'in_progress' | 'observed' | 'stalled';
  evidence_note?: string;
  target_review_month?: string;
}): Promise<ProofPoint> => {
  const response = await apiClient.patch<ApiResponse<ProofPoint>>(`/proof-points/${id}`, data);
  return response.data.data;
};

export const deleteProofPoint = async (id: string): Promise<void> => {
  await apiClient.delete(`/proof-points/${id}`);
};

// Attachment Operations
export const uploadAttachment = async (file: File, options: {
  proof_point_id?: string;
  monthly_review_id?: string;
  label?: string;
}): Promise<Attachment> => {
  const formData = new FormData();
  formData.append('file', file);
  if (options.proof_point_id) formData.append('proof_point_id', options.proof_point_id);
  if (options.monthly_review_id) formData.append('monthly_review_id', options.monthly_review_id);
  if (options.label) formData.append('label', options.label);

  const response = await apiClient.post<ApiResponse<Attachment>>('/attachments', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data.data;
};

export const downloadAttachment = async (id: string): Promise<Blob> => {
  const response = await apiClient.get(`/attachments/${id}`, { responseType: 'blob' });
  return response.data;
};

export const deleteAttachment = async (id: string): Promise<void> => {
  await apiClient.delete(`/attachments/${id}`);
};