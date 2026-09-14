import { apiClient } from "./client";
import { Machine, MachineCreate, MachineUpdate } from "./types";

export const machinesApi = {
  list: async (): Promise<Machine[]> => {
    const res = await apiClient.get<Machine[]>("/machines");
    return res.data;
  },

  get: async (id: string): Promise<Machine> => {
    const res = await apiClient.get<Machine>(`/machines/${id}`);
    return res.data;
  },

  create: async (data: MachineCreate): Promise<Machine> => {
    const res = await apiClient.post<Machine>("/machines", data);
    return res.data;
  },

  update: async (id: string, data: MachineUpdate): Promise<Machine> => {
    const res = await apiClient.put<Machine>(`/machines/${id}`, data);
    return res.data;
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/machines/${id}`);
  },
};
