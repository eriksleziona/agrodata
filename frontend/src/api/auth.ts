import { apiClient } from "./client";
import { LoginRequest, RegisterRequest, TokenResponse, User } from "./types";

export const authApi = {
  login: async (data: LoginRequest): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>("/auth/login", data);
    return res.data;
  },

  register: async (data: RegisterRequest): Promise<User> => {
    const res = await apiClient.post<User>("/auth/register", data);
    return res.data;
  },

  getMe: async (): Promise<User> => {
    const res = await apiClient.get<User>("/auth/me");
    return res.data;
  },
};
