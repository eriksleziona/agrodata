import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Sprout, Lock, Mail, Building } from "lucide-react";
import { authApi } from "../api/auth";
import { useAuthStore } from "../store/useAuthStore";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { ErrorAlert } from "../components/ui/Error";

export const Login: React.FC = () => {
  const navigate = useNavigate();
  const { login, setUser } = useAuthStore();

  const [organizationId, setOrganizationId] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const tokenRes = await authApi.login({
        organization_id: organizationId.trim(),
        email: email.trim(),
        password,
      });

      login(tokenRes.access_token);

      // Fetch user profile
      const userProfile = await authApi.getMe();
      setUser(userProfile);

      navigate("/dashboard");
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      const message =
        axiosError.response?.data?.detail ||
        "Authentication failed. Please verify your Organization ID, email, and password.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 px-4 py-12 select-none">
      <div className="max-w-md w-full">
        {/* Brand Banner */}
        <div className="text-center mb-8">
          <div className="inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-tr from-agro-600 to-agro-500 text-white shadow-xl shadow-agro-950/50 ring-4 ring-slate-800 mb-4">
            <Sprout className="w-8 h-8" />
          </div>
          <h2 className="text-2xl font-bold text-white tracking-tight">
            Sign in to AgroData
          </h2>
          <p className="mt-1.5 text-xs text-slate-400">
            Agricultural Intelligence & Telemetry Platform
          </p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl p-8 shadow-2xl border border-slate-200/80">
          {error && (
            <div className="mb-6">
              <ErrorAlert message={error} />
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Organization ID"
              placeholder="e.g. 123e4567-e89b-12d3-a456-426614174000"
              required
              value={organizationId}
              onChange={(e) => setOrganizationId(e.target.value)}
              leftIcon={<Building className="w-4 h-4" />}
              helperText="Enter your tenant organization UUID."
            />

            <Input
              label="Email Address"
              type="email"
              placeholder="operator@farm.com"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              leftIcon={<Mail className="w-4 h-4" />}
            />

            <Input
              label="Password"
              type="password"
              placeholder="••••••••"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              leftIcon={<Lock className="w-4 h-4" />}
            />

            <div className="pt-2">
              <Button
                type="submit"
                variant="primary"
                size="lg"
                className="w-full"
                isLoading={isLoading}
              >
                Sign In
              </Button>
            </div>
          </form>

          {/* Demonstration Notice */}
          <div className="mt-6 pt-5 border-t border-slate-100 text-center text-xs text-slate-500">
            <span>Need an account? Contact your tenant administrator.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
