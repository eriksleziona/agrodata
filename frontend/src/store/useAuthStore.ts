import { create } from "zustand";
import { User } from "../api/types";
import { authApi } from "../api/auth";

interface AuthState {
  token: string | null;
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string, user?: User) => void;
  setUser: (user: User) => void;
  logout: () => void;
  initialize: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  token: localStorage.getItem("agrodata_token"),
  user: null,
  isAuthenticated: !!localStorage.getItem("agrodata_token"),
  isLoading: true,

  login: (token: string, user?: User) => {
    localStorage.setItem("agrodata_token", token);
    set({
      token,
      user: user || null,
      isAuthenticated: true,
      isLoading: false,
    });
  },

  setUser: (user: User) => {
    set({ user });
  },

  logout: () => {
    localStorage.removeItem("agrodata_token");
    set({
      token: null,
      user: null,
      isAuthenticated: false,
      isLoading: false,
    });
  },

  initialize: async () => {
    const token = get().token;
    if (!token) {
      set({ isLoading: false, isAuthenticated: false, user: null });
      return;
    }

    try {
      const user = await authApi.getMe();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem("agrodata_token");
      set({
        token: null,
        user: null,
        isAuthenticated: false,
        isLoading: false,
      });
    }
  },
}));
