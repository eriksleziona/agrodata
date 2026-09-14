import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Tractor, Plus, Trash2, Search, Cpu } from "lucide-react";
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
import { MachineCreate } from "../api/types";

export const Machines: React.FC = () => {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);

  // Form state
  const [name, setName] = useState("");
  const [manufacturer, setManufacturer] = useState("");
  const [model, setModel] = useState("");
  const [serialNumber, setSerialNumber] = useState("");
  const [year, setYear] = useState<string>("");
  const [powerHp, setPowerHp] = useState<string>("");
  const [deviceId, setDeviceId] = useState("");

  const {
    data: machines = [],
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["machines"],
    queryFn: machinesApi.list,
  });

  const createMutation = useMutation({
    mutationFn: machinesApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["machines"] });
      setIsModalOpen(false);
      resetForm();
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrorBanner(
        axiosError.response?.data?.detail || "Failed to register machine.",
      );
    },
  });

  const deleteMutation = useMutation({
    mutationFn: machinesApi.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["machines"] });
    },
    onError: (err: unknown) => {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      setErrorBanner(
        axiosError.response?.data?.detail || "Failed to delete machine.",
      );
    },
  });

  const resetForm = () => {
    setName("");
    setManufacturer("");
    setModel("");
    setSerialNumber("");
    setYear("");
    setPowerHp("");
    setDeviceId("");
    setErrorBanner(null);
  };

  const handleCreate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !user?.organization_id) return;

    const payload: MachineCreate = {
      organization_id: user.organization_id,
      name: name.trim(),
      manufacturer: manufacturer.trim() || undefined,
      model: model.trim() || undefined,
      serial_number: serialNumber.trim() || undefined,
      year: year ? parseInt(year, 10) : undefined,
      power_hp: powerHp ? parseInt(powerHp, 10) : undefined,
      device_id: deviceId.trim() || undefined,
    };

    createMutation.mutate(payload);
  };

  const handleDelete = (id: string, machineName: string) => {
    if (window.confirm(`Are you sure you want to delete ${machineName}?`)) {
      deleteMutation.mutate(id);
    }
  };

  const filteredMachines = machines.filter(
    (m) =>
      m.name.toLowerCase().includes(search.toLowerCase()) ||
      (m.manufacturer &&
        m.manufacturer.toLowerCase().includes(search.toLowerCase())) ||
      (m.device_id && m.device_id.toLowerCase().includes(search.toLowerCase())),
  );

  if (isLoading) {
    return <PageLoading message="Loading machinery fleet..." />;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Machinery Fleet
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Registered tractors, harvesters, and edge telematics devices.
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          onClick={() => {
            resetForm();
            setIsModalOpen(true);
          }}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Register Machine
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
          title="Could not retrieve machines"
          message="Failed to load machines from backend API."
          onRetry={() => refetch()}
        />
      )}

      {/* Filter Bar */}
      <div className="flex items-center gap-3">
        <div className="max-w-md w-full">
          <Input
            placeholder="Search by machine name, brand, or edge device ID..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />
        </div>
      </div>

      {/* Machines Table */}
      {filteredMachines.length === 0 ? (
        <EmptyState
          icon={<Tractor className="w-8 h-8" />}
          title="No machines found"
          description={
            search
              ? "No machines matched your search criteria."
              : "Add your first tractor or harvester to connect telematics devices."
          }
          actionText="Register First Machine"
          onAction={() => {
            resetForm();
            setIsModalOpen(true);
          }}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Machine Name</TableHead>
              <TableHead>Manufacturer / Model</TableHead>
              <TableHead>Power</TableHead>
              <TableHead>Year</TableHead>
              <TableHead>Serial Number</TableHead>
              <TableHead>Telematics Node</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredMachines.map((machine) => (
              <TableRow key={machine.id}>
                <TableCell className="font-semibold text-slate-900">
                  <div className="flex items-center gap-2.5">
                    <div className="h-8 w-8 rounded-lg bg-agro-50 text-agro-700 flex items-center justify-center shrink-0">
                      <Tractor className="w-4 h-4" />
                    </div>
                    <span>{machine.name}</span>
                  </div>
                </TableCell>
                <TableCell className="text-slate-600">
                  {machine.manufacturer || "—"}{" "}
                  {machine.model ? `(${machine.model})` : ""}
                </TableCell>
                <TableCell className="font-mono text-xs text-slate-700">
                  {machine.power_hp ? `${machine.power_hp} HP` : "—"}
                </TableCell>
                <TableCell className="text-slate-600 text-xs">
                  {machine.year || "—"}
                </TableCell>
                <TableCell className="font-mono text-xs text-slate-500">
                  {machine.serial_number || "—"}
                </TableCell>
                <TableCell>
                  {machine.device_id ? (
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-mono font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
                      <Cpu className="w-3 h-3 text-emerald-600" />
                      {machine.device_id}
                    </span>
                  ) : (
                    <span className="text-xs text-slate-400">Unpaired</span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDelete(machine.id, machine.name)}
                    className="text-slate-400 hover:text-red-600 p-1.5"
                    title="Delete Machine"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}

      {/* Add Machine Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Register New Machine"
        description="Add a machine to your tenant fleet and pair an IoT telemetry box."
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={handleCreate}
              isLoading={createMutation.isPending}
            >
              Save Machine
            </Button>
          </>
        }
      >
        <form onSubmit={handleCreate} className="space-y-4">
          <Input
            label="Machine Display Name"
            placeholder="e.g. Claas Lexion 8900"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Manufacturer"
              placeholder="e.g. Claas, John Deere"
              value={manufacturer}
              onChange={(e) => setManufacturer(e.target.value)}
            />
            <Input
              label="Model"
              placeholder="e.g. 8900, 8R 410"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <Input
              label="Power (HP)"
              type="number"
              placeholder="e.g. 410"
              value={powerHp}
              onChange={(e) => setPowerHp(e.target.value)}
            />
            <Input
              label="Year"
              type="number"
              placeholder="e.g. 2024"
              value={year}
              onChange={(e) => setYear(e.target.value)}
            />
            <Input
              label="Serial Number"
              placeholder="e.g. SN-998811"
              value={serialNumber}
              onChange={(e) => setSerialNumber(e.target.value)}
            />
          </div>

          <Input
            label="Telematics Box Device ID"
            placeholder="e.g. EDGE-BOX-001"
            value={deviceId}
            onChange={(e) => setDeviceId(e.target.value)}
            leftIcon={<Cpu className="w-4 h-4" />}
            helperText="Unique hardware ID for edge telemetry ingestion."
          />
        </form>
      </Modal>
    </div>
  );
};
