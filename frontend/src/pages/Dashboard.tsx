import React from "react";
import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import {
  Tractor,
  ClipboardList,
  Grid3X3,
  Activity,
  Plus,
  ArrowUpRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  PlayCircle,
  PauseCircle,
} from "lucide-react";
import { machinesApi } from "../api/machines";
import { jobsApi } from "../api/jobs";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { PageLoading } from "../components/ui/Loading";
import { ErrorAlert } from "../components/ui/Error";
import { JobStatus } from "../api/types";

const statusBadgeStyles: Record<
  JobStatus,
  { label: string; bg: string; text: string; icon: React.ElementType }
> = {
  PLANNED: {
    label: "Planned",
    bg: "bg-slate-100",
    text: "text-slate-700",
    icon: Clock,
  },
  STARTED: {
    label: "In Progress",
    bg: "bg-emerald-100",
    text: "text-emerald-800",
    icon: PlayCircle,
  },
  PAUSED: {
    label: "Paused",
    bg: "bg-amber-100",
    text: "text-amber-800",
    icon: PauseCircle,
  },
  COMPLETED: {
    label: "Completed",
    bg: "bg-blue-100",
    text: "text-blue-800",
    icon: CheckCircle2,
  },
  CANCELLED: {
    label: "Cancelled",
    bg: "bg-red-100",
    text: "text-red-700",
    icon: AlertCircle,
  },
};

export const Dashboard: React.FC = () => {
  const {
    data: machines = [],
    isLoading: isMachinesLoading,
    error: machinesError,
  } = useQuery({
    queryKey: ["machines"],
    queryFn: machinesApi.list,
  });

  const {
    data: jobs = [],
    isLoading: isJobsLoading,
    error: jobsError,
  } = useQuery({
    queryKey: ["jobs"],
    queryFn: () => jobsApi.list(),
  });

  if (isMachinesLoading || isJobsLoading) {
    return <PageLoading message="Loading operational dashboard..." />;
  }

  const activeJobs = jobs.filter((j) => j.status === "STARTED");
  const completedJobs = jobs.filter((j) => j.status === "COMPLETED");
  const totalFuelUsed = jobs.reduce((acc, j) => acc + (j.fuel_used || 0), 0);
  const totalAreaCompleted = jobs.reduce(
    (acc, j) => acc + (j.area_completed || 0),
    0,
  );

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Operational Dashboard
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Real-time telemetry overview, machine status, and service activity.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/machines">
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Plus className="w-4 h-4" />}
            >
              Add Machine
            </Button>
          </Link>
          <Link to="/jobs">
            <Button
              variant="primary"
              size="sm"
              leftIcon={<Plus className="w-4 h-4" />}
            >
              New Job
            </Button>
          </Link>
        </div>
      </div>

      {(machinesError || jobsError) && (
        <ErrorAlert
          title="Data synchronization warning"
          message="Could not load latest telemetry data. Displaying cached records."
        />
      )}

      {/* KPI Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card className="border-l-4 border-l-agro-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                Fleet Machines
              </p>
              <h4 className="text-2xl font-bold text-slate-900 mt-1">
                {machines.length}
              </h4>
              <p className="text-[11px] text-agro-700 font-medium mt-1">
                {machines.filter((m) => !!m.device_id).length} edge-connected
              </p>
            </div>
            <div className="h-12 w-12 rounded-xl bg-agro-50 text-agro-600 flex items-center justify-center">
              <Tractor className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-emerald-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                Active Operations
              </p>
              <h4 className="text-2xl font-bold text-slate-900 mt-1">
                {activeJobs.length}
              </h4>
              <p className="text-[11px] text-emerald-700 font-medium mt-1">
                {jobs.length} total operations
              </p>
            </div>
            <div className="h-12 w-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <Activity className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                Area Completed
              </p>
              <h4 className="text-2xl font-bold text-slate-900 mt-1">
                {totalAreaCompleted.toFixed(1)}{" "}
                <span className="text-sm font-normal text-slate-500">ha</span>
              </h4>
              <p className="text-[11px] text-blue-700 font-medium mt-1">
                {completedJobs.length} completed operations
              </p>
            </div>
            <div className="h-12 w-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
              <Grid3X3 className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-amber-500">
          <CardContent className="p-5 flex items-center justify-between">
            <div>
              <p className="text-xs font-medium text-slate-500 uppercase tracking-wider">
                Fuel Consumed
              </p>
              <h4 className="text-2xl font-bold text-slate-900 mt-1">
                {totalFuelUsed.toFixed(0)}{" "}
                <span className="text-sm font-normal text-slate-500">L</span>
              </h4>
              <p className="text-[11px] text-amber-700 font-medium mt-1">
                Avg{" "}
                {(totalAreaCompleted
                  ? totalFuelUsed / totalAreaCompleted
                  : 0
                ).toFixed(1)}{" "}
                L/ha
              </p>
            </div>
            <div className="h-12 w-12 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center">
              <ClipboardList className="w-6 h-6" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid: Recent Operations & Fleet Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Jobs */}
        <div className="lg:col-span-2 space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle>Recent Agricultural Jobs</CardTitle>
                <CardDescription>
                  Status of active and scheduled field operations.
                </CardDescription>
              </div>
              <Link to="/jobs">
                <Button
                  variant="ghost"
                  size="sm"
                  rightIcon={<ArrowUpRight className="w-4 h-4" />}
                >
                  View All
                </Button>
              </Link>
            </CardHeader>
            <CardContent className="p-0">
              {jobs.length === 0 ? (
                <div className="p-8 text-center text-sm text-slate-500">
                  No jobs planned yet. Click "New Job" to schedule your first
                  operation.
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {jobs.slice(0, 5).map((job) => {
                    const badge =
                      statusBadgeStyles[job.status] ||
                      statusBadgeStyles.PLANNED;
                    const StatusIcon = badge.icon;
                    return (
                      <div
                        key={job.id}
                        className="p-4 flex items-center justify-between hover:bg-slate-50/80 transition-colors"
                      >
                        <div className="flex items-center gap-3.5">
                          <div className="h-10 w-10 rounded-lg bg-slate-100 flex items-center justify-center text-slate-600 font-bold text-xs uppercase">
                            {job.type.slice(0, 3)}
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold text-slate-800">
                              {job.type}
                            </h4>
                            <p className="text-xs text-slate-500">
                              Planned:{" "}
                              {job.area_planned
                                ? `${job.area_planned} ha`
                                : "Unspecified"}{" "}
                              • Done: {job.area_completed} ha
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span
                            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold ${badge.bg} ${badge.text}`}
                          >
                            <StatusIcon className="w-3.5 h-3.5" />
                            {badge.label}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Fleet Machines Overview */}
        <div className="space-y-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-3">
              <div>
                <CardTitle>Fleet Summary</CardTitle>
                <CardDescription>
                  Registered tractors and equipment.
                </CardDescription>
              </div>
              <Link to="/machines">
                <Button
                  variant="ghost"
                  size="sm"
                  rightIcon={<ArrowUpRight className="w-4 h-4" />}
                >
                  View All
                </Button>
              </Link>
            </CardHeader>
            <CardContent className="p-0">
              {machines.length === 0 ? (
                <div className="p-8 text-center text-sm text-slate-500">
                  No machines added yet.
                </div>
              ) : (
                <div className="divide-y divide-slate-100">
                  {machines.slice(0, 5).map((machine) => (
                    <div
                      key={machine.id}
                      className="p-4 flex items-center justify-between hover:bg-slate-50/80 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="h-9 w-9 rounded-lg bg-agro-50 text-agro-700 flex items-center justify-center">
                          <Tractor className="w-5 h-5" />
                        </div>
                        <div>
                          <h4 className="text-sm font-semibold text-slate-800">
                            {machine.name}
                          </h4>
                          <p className="text-xs text-slate-500">
                            {machine.manufacturer || "Custom"}{" "}
                            {machine.model || ""}
                          </p>
                        </div>
                      </div>
                      <div>
                        {machine.device_id ? (
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
                            Online
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-500">
                            No Box
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
