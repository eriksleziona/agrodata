import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ClipboardList,
  Plus,
  Play,
  Pause,
  RotateCw,
  CheckCircle,
  XCircle,
  Clock,
  PlayCircle,
  PauseCircle,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";
import { jobsApi } from "../api/jobs";
import { machinesApi } from "../api/machines";
import { useAuthStore } from "../store/useAuthStore";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/Table";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { Modal } from "../components/ui/Modal";
import { EmptyState } from "../components/ui/EmptyState";
import { PageLoading } from "../components/ui/Loading";
import { ErrorAlert } from "../components/ui/Error";
import { Job, JobCreate, JobFinish, JobStatus } from "../api/types";

const statusBadgeStyles: Record<
  JobStatus,
  { label: string; bg: string; text: string; icon: React.ElementType }
> = {
  PLANNED: {
    label: "Planned",
    bg: "bg-slate-100 border-slate-200",
    text: "text-slate-700",
    icon: Clock,
  },
  STARTED: {
    label: "In Progress",
    bg: "bg-emerald-50 border-emerald-200",
    text: "text-emerald-800",
    icon: PlayCircle,
  },
  PAUSED: {
    label: "Paused",
    bg: "bg-amber-50 border-amber-200",
    text: "text-amber-800",
    icon: PauseCircle,
  },
  COMPLETED: {
    label: "Completed",
    bg: "bg-blue-50 border-blue-200",
    text: "text-blue-800",
    icon: CheckCircle2,
  },
  CANCELLED: {
    label: "Cancelled",
    bg: "bg-red-50 border-red-200",
    text: "text-red-700",
    icon: AlertCircle,
  },
};

export const Jobs: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();

  const [selectedStatus, setSelectedStatus] = useState<JobStatus | "ALL">(
    "ALL",
  );
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [finishModalJob, setFinishModalJob] = useState<Job | null>(null);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // New Job Form State
  const [jobType, setJobType] = useState("HARVESTING");
  const [areaPlanned, setAreaPlanned] = useState("");
  const [selectedMachineId, setSelectedMachineId] = useState("");

  // Finish Job Metrics Form State
  const [areaCompleted, setAreaCompleted] = useState("");
  const [distanceMeters, setDistanceMeters] = useState("");
  const [workingSeconds, setWorkingSeconds] = useState("");
  const [fuelUsedLiters, setFuelUsedLiters] = useState("");

  const {
    data: jobs = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["jobs", selectedStatus],
    queryFn: () =>
      jobsApi.list(selectedStatus === "ALL" ? undefined : selectedStatus),
  });

  const { data: machines = [] } = useQuery({
    queryKey: ["machines"],
    queryFn: machinesApi.list,
  });

  // Mutations for state transitions
  const createMutation = useMutation({
    mutationFn: jobsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      setIsCreateModalOpen(false);
      resetCreateForm();
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrorBanner(
        axiosError.response?.data?.detail || "Failed to create job.",
      );
    },
  });

  const startMutation = useMutation({
    mutationFn: (id: string) => jobsApi.start(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrorBanner(
        axiosError.response?.data?.detail || "Failed to start job.",
      );
    },
  });

  const pauseMutation = useMutation({
    mutationFn: (id: string) => jobsApi.pause(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrorBanner(
        axiosError.response?.data?.detail || "Failed to pause job.",
      );
    },
  });

  const resumeMutation = useMutation({
    mutationFn: (id: string) => jobsApi.resume(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrorBanner(
        axiosError.response?.data?.detail || "Failed to resume job.",
      );
    },
  });

  const finishMutation = useMutation({
    mutationFn: ({ id, metrics }: { id: string; metrics: JobFinish }) =>
      jobsApi.finish(id, metrics),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["jobs"] });
      setFinishModalJob(null);
      resetFinishForm();
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrorBanner(
        axiosError.response?.data?.detail || "Failed to complete job.",
      );
    },
  });

  const cancelMutation = useMutation({
    mutationFn: (id: string) => jobsApi.cancel(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["jobs"] }),
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrorBanner(
        axiosError.response?.data?.detail || "Failed to cancel job.",
      );
    },
  });

  const resetCreateForm = () => {
    setJobType("HARVESTING");
    setAreaPlanned("");
    setSelectedMachineId("");
    setErrorBanner(null);
  };

  const resetFinishForm = () => {
    setAreaCompleted("");
    setDistanceMeters("");
    setWorkingSeconds("");
    setFuelUsedLiters("");
  };

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.organization_id || !jobType) return;

    const payload: JobCreate = {
      organization_id: user.organization_id,
      type: jobType,
      area_planned: areaPlanned ? parseFloat(areaPlanned) : undefined,
      machine_id: selectedMachineId || undefined,
    };

    createMutation.mutate(payload);
  };

  const handleFinishSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!finishModalJob) return;

    const metrics: JobFinish = {
      area_completed: areaCompleted
        ? parseFloat(areaCompleted)
        : finishModalJob.area_planned || 0,
      distance: distanceMeters ? parseFloat(distanceMeters) : 0,
      working_time: workingSeconds ? parseInt(workingSeconds, 10) : 0,
      fuel_used: fuelUsedLiters ? parseFloat(fuelUsedLiters) : 0,
    };

    finishMutation.mutate({ id: finishModalJob.id, metrics });
  };

  if (isLoading) {
    return <PageLoading message="Loading agricultural jobs..." />;
  }

  const statusOptions: (JobStatus | "ALL")[] = [
    "ALL",
    "PLANNED",
    "STARTED",
    "PAUSED",
    "COMPLETED",
    "CANCELLED",
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Agricultural Operations & Jobs
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Schedule, monitor, and transition field service operations through
            their lifecycle.
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            resetCreateForm();
            setIsCreateModalOpen(true);
          }}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Plan New Job
        </Button>
      </div>

      {errorBanner && (
        <ErrorAlert
          message={errorBanner}
          onRetry={() => setErrorBanner(null)}
        />
      )}

      {error && (
        <ErrorAlert
          title="Could not load jobs"
          message="Failed to retrieve jobs from the server."
          onRetry={() => refetch()}
        />
      )}

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2 pb-1 border-b border-slate-200">
        {statusOptions.map((st) => (
          <button
            key={st}
            onClick={() => setSelectedStatus(st)}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
              selectedStatus === st
                ? "bg-agro-600 text-white shadow-xs"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {st === "ALL" ? "All Operations" : st}
          </button>
        ))}
      </div>

      {/* Jobs Table */}
      {jobs.length === 0 ? (
        <EmptyState
          icon={<ClipboardList className="w-8 h-8" />}
          title="No jobs found"
          description={
            selectedStatus !== "ALL"
              ? `No operations currently have the '${selectedStatus}' status.`
              : "Create your first agricultural operation to start tracking field progress."
          }
          actionText="Plan First Operation"
          onAction={() => setIsCreateModalOpen(true)}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Operation Type</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Area Planned / Done</TableHead>
              <TableHead>Assigned Machine</TableHead>
              <TableHead>Working Time</TableHead>
              <TableHead>Fuel Used</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {jobs.map((job) => {
              const badge =
                statusBadgeStyles[job.status] || statusBadgeStyles.PLANNED;
              const StatusIcon = badge.icon;
              const machine = machines.find((m) => m.id === job.machine_id);

              return (
                <TableRow key={job.id}>
                  <TableCell className="font-semibold text-slate-900">
                    <div className="flex items-center gap-2.5">
                      <div className="h-8 w-8 rounded-lg bg-agro-50 text-agro-700 flex items-center justify-center font-bold text-xs uppercase shrink-0">
                        {job.type.slice(0, 3)}
                      </div>
                      <div>
                        <div>{job.type}</div>
                        <div className="text-[10px] text-slate-400 font-mono">
                          ID: #{job.id.slice(0, 8)}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border ${badge.bg} ${badge.text}`}
                    >
                      <StatusIcon className="w-3.5 h-3.5" />
                      {badge.label}
                    </span>
                  </TableCell>
                  <TableCell className="text-xs">
                    <div className="font-medium text-slate-800">
                      {job.area_completed} ha
                    </div>
                    <div className="text-slate-400 text-[11px]">
                      Planned:{" "}
                      {job.area_planned ? `${job.area_planned} ha` : "—"}
                    </div>
                  </TableCell>
                  <TableCell className="text-xs text-slate-600">
                    {machine ? machine.name : "—"}
                  </TableCell>
                  <TableCell className="text-xs text-slate-600 font-mono">
                    {job.working_time
                      ? `${Math.floor(job.working_time / 60)} min`
                      : "0 min"}
                  </TableCell>
                  <TableCell className="text-xs text-slate-600 font-mono">
                    {job.fuel_used ? `${job.fuel_used} L` : "0 L"}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      {/* State transition triggers */}
                      {job.status === "PLANNED" && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => startMutation.mutate(job.id)}
                          leftIcon={
                            <Play className="w-3.5 h-3.5 text-emerald-600" />
                          }
                          className="hover:bg-emerald-50 hover:border-emerald-200 text-xs"
                        >
                          Start
                        </Button>
                      )}

                      {job.status === "STARTED" && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => pauseMutation.mutate(job.id)}
                            leftIcon={
                              <Pause className="w-3.5 h-3.5 text-amber-600" />
                            }
                            className="hover:bg-amber-50 hover:border-amber-200 text-xs"
                          >
                            Pause
                          </Button>
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => setFinishModalJob(job)}
                            leftIcon={<CheckCircle className="w-3.5 h-3.5" />}
                            className="text-xs bg-blue-600 hover:bg-blue-700"
                          >
                            Finish
                          </Button>
                        </>
                      )}

                      {job.status === "PAUSED" && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => resumeMutation.mutate(job.id)}
                            leftIcon={
                              <RotateCw className="w-3.5 h-3.5 text-emerald-600" />
                            }
                            className="hover:bg-emerald-50 hover:border-emerald-200 text-xs"
                          >
                            Resume
                          </Button>
                          <Button
                            variant="primary"
                            size="sm"
                            onClick={() => setFinishModalJob(job)}
                            leftIcon={<CheckCircle className="w-3.5 h-3.5" />}
                            className="text-xs bg-blue-600 hover:bg-blue-700"
                          >
                            Finish
                          </Button>
                        </>
                      )}

                      {(job.status === "PLANNED" ||
                        job.status === "STARTED" ||
                        job.status === "PAUSED") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            if (
                              window.confirm(
                                "Are you sure you want to cancel this operation?",
                              )
                            ) {
                              cancelMutation.mutate(job.id);
                            }
                          }}
                          className="text-slate-400 hover:text-red-600 p-1.5"
                          title="Cancel Job"
                        >
                          <XCircle className="w-4 h-4" />
                        </Button>
                      )}

                      {(job.status === "COMPLETED" ||
                        job.status === "CANCELLED") && (
                        <span className="text-[11px] text-slate-400 italic">
                          Terminal
                        </span>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {/* Plan New Job Modal */}
      <Modal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        title="Plan Field Operation"
        description="Schedule an agricultural operation with assigned machinery."
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsCreateModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleCreate}
              isLoading={createMutation.isPending}
            >
              Save Job
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 tracking-wide uppercase mb-1.5">
              Operation Type *
            </label>
            <select
              value={jobType}
              onChange={(e) => setJobType(e.target.value)}
              className="block w-full rounded-lg border border-slate-300 text-sm py-2 px-3 focus:outline-none focus:ring-2 focus:ring-agro-100 focus:border-agro-500"
            >
              <option value="HARVESTING">Harvesting</option>
              <option value="SEEDING">Seeding / Sowing</option>
              <option value="PLOWING">Plowing</option>
              <option value="SPRAYING">Spraying</option>
              <option value="TILLAGE">Tillage</option>
              <option value="FERTILIZING">Fertilizing</option>
            </select>
          </div>

          <Input
            label="Planned Area (Hectares)"
            type="number"
            step="0.1"
            placeholder="e.g. 24.5"
            value={areaPlanned}
            onChange={(e) => setAreaPlanned(e.target.value)}
          />

          <div>
            <label className="block text-xs font-semibold text-slate-700 tracking-wide uppercase mb-1.5">
              Assigned Fleet Machine
            </label>
            <select
              value={selectedMachineId}
              onChange={(e) => setSelectedMachineId(e.target.value)}
              className="block w-full rounded-lg border border-slate-300 text-sm py-2 px-3 focus:outline-none focus:ring-2 focus:ring-agro-100 focus:border-agro-500"
            >
              <option value="">No machine assigned</option>
              {machines.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.name} {m.model ? `(${m.model})` : ""}
                </option>
              ))}
            </select>
          </div>
        </form>
      </Modal>

      {/* Finish Job Modal */}
      <Modal
        isOpen={!!finishModalJob}
        onClose={() => setFinishModalJob(null)}
        title="Complete Operation Summary"
        description="Enter closing telematics metrics and completed area to complete this job."
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setFinishModalJob(null)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleFinishSubmit}
              isLoading={finishMutation.isPending}
            >
              Mark Completed
            </Button>
          </>
        }
      >
        <form onSubmit={handleFinishSubmit} className="space-y-4">
          <Input
            label="Area Completed (Hectares)"
            type="number"
            step="0.1"
            placeholder={
              finishModalJob?.area_planned
                ? String(finishModalJob.area_planned)
                : "e.g. 24.5"
            }
            value={areaCompleted}
            onChange={(e) => setAreaCompleted(e.target.value)}
          />

          <div className="grid grid-cols-3 gap-3">
            <Input
              label="Distance (Meters)"
              type="number"
              placeholder="e.g. 8400"
              value={distanceMeters}
              onChange={(e) => setDistanceMeters(e.target.value)}
            />
            <Input
              label="Working (Seconds)"
              type="number"
              placeholder="e.g. 7200"
              value={workingSeconds}
              onChange={(e) => setWorkingSeconds(e.target.value)}
            />
            <Input
              label="Fuel Used (Liters)"
              type="number"
              step="0.1"
              placeholder="e.g. 35.5"
              value={fuelUsedLiters}
              onChange={(e) => setFuelUsedLiters(e.target.value)}
            />
          </div>
        </form>
      </Modal>
    </div>
  );
};
