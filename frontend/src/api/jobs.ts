import { apiClient } from "./client";
import { Job, JobCreate, JobFinish, JobStatus } from "./types";

export const jobsApi = {
  list: async (status?: JobStatus): Promise<Job[]> => {
    const params = status ? { status } : {};
    const res = await apiClient.get<Job[]>("/jobs", { params });
    return res.data;
  },

  get: async (id: string): Promise<Job> => {
    const res = await apiClient.get<Job>(`/jobs/${id}`);
    return res.data;
  },

  create: async (data: JobCreate): Promise<Job> => {
    const res = await apiClient.post<Job>("/jobs", data);
    return res.data;
  },

  start: async (id: string): Promise<Job> => {
    const res = await apiClient.post<Job>(`/jobs/${id}/start`);
    return res.data;
  },

  pause: async (id: string): Promise<Job> => {
    const res = await apiClient.post<Job>(`/jobs/${id}/pause`);
    return res.data;
  },

  resume: async (id: string): Promise<Job> => {
    const res = await apiClient.post<Job>(`/jobs/${id}/resume`);
    return res.data;
  },

  finish: async (id: string, metrics?: JobFinish): Promise<Job> => {
    const res = await apiClient.post<Job>(`/jobs/${id}/finish`, metrics || {});
    return res.data;
  },

  cancel: async (id: string): Promise<Job> => {
    const res = await apiClient.post<Job>(`/jobs/${id}/cancel`);
    return res.data;
  },
};
