import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute, PublicRoute } from "./ProtectedRoute";
import { DashboardLayout } from "../components/layout/DashboardLayout";
import { Login } from "../pages/Login";
import { Dashboard } from "../pages/Dashboard";
import { Farms } from "../pages/Farms";
import { Fields } from "../pages/Fields";
import { Machines } from "../pages/Machines";
import { Jobs } from "../pages/Jobs";

export const router = createBrowserRouter([
  {
    path: "/login",
    element: (
      <PublicRoute>
        <Login />
      </PublicRoute>
    ),
  },
  {
    element: <ProtectedRoute />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          {
            path: "/",
            element: <Navigate to="/dashboard" replace />,
          },
          {
            path: "/dashboard",
            element: <Dashboard />,
          },
          {
            path: "/farms",
            element: <Farms />,
          },
          {
            path: "/fields",
            element: <Fields />,
          },
          {
            path: "/machines",
            element: <Machines />,
          },
          {
            path: "/jobs",
            element: <Jobs />,
          },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/dashboard" replace />,
  },
]);
