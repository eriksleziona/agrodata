import React, { useState } from "react";
import { Warehouse, Plus, Search, MapPin } from "lucide-react";
import { Card, CardContent } from "../components/ui/Card";
import { Button } from "../components/ui/Button";
import { Input } from "../components/ui/Input";
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { Farm } from "../api/types";

const mockFarms: Farm[] = [
  {
    id: "1",
    name: "Green Valley Agriculture",
    code: "FARM-GV-01",
    location: "Wielkopolskie, Poland",
    total_area_ha: 420.5,
    active_fields_count: 14,
    created_at: "2026-03-01T10:00:00Z",
  },
  {
    id: "2",
    name: "Baltic Harvest Estates",
    code: "FARM-BH-02",
    location: "Pomorskie, Poland",
    total_area_ha: 850.0,
    active_fields_count: 28,
    created_at: "2026-04-15T08:30:00Z",
  },
  {
    id: "3",
    name: "Silesian Sun Agribusiness",
    code: "FARM-SS-03",
    location: "Dolnośląskie, Poland",
    total_area_ha: 310.2,
    active_fields_count: 9,
    created_at: "2026-05-10T12:00:00Z",
  },
];

export const Farms: React.FC = () => {
  const [farms, setFarms] = useState<Farm[]>(mockFarms);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newFarmName, setNewFarmName] = useState("");
  const [newFarmLocation, setNewFarmLocation] = useState("");
  const [newFarmArea, setNewFarmArea] = useState("");

  const filteredFarms = farms.filter(
    (f) =>
      f.name.toLowerCase().includes(search.toLowerCase()) ||
      f.location.toLowerCase().includes(search.toLowerCase()) ||
      f.code.toLowerCase().includes(search.toLowerCase()),
  );

  const handleAddFarm = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newFarmName) return;

    const newFarm: Farm = {
      id: String(Date.now()),
      name: newFarmName,
      code: `FARM-${newFarmName.slice(0, 2).toUpperCase()}-${Math.floor(10 + Math.random() * 90)}`,
      location: newFarmLocation || "Unspecified Location",
      total_area_ha: parseFloat(newFarmArea) || 0,
      active_fields_count: 0,
      created_at: new Date().toISOString(),
    };

    setFarms([newFarm, ...farms]);
    setIsModalOpen(false);
    setNewFarmName("");
    setNewFarmLocation("");
    setNewFarmArea("");
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Farm Estates
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Manage organization farms, estate boundaries, and parcel aggregates.
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          onClick={() => setIsModalOpen(true)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Farm
        </Button>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-3">
        <div className="max-w-md w-full">
          <Input
            placeholder="Search farms by name, code, or location..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />
        </div>
      </div>

      {/* Farms Grid */}
      {filteredFarms.length === 0 ? (
        <EmptyState
          icon={<Warehouse className="w-8 h-8" />}
          title="No farms found"
          description={
            search
              ? "No farm estates matched your search criteria."
              : "Get started by creating your first farm estate."
          }
          actionText="Add New Farm"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredFarms.map((farm) => (
            <Card key={farm.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-5 space-y-4">
                <div className="flex items-start justify-between">
                  <div className="h-10 w-10 rounded-xl bg-agro-50 text-agro-700 flex items-center justify-center font-bold">
                    <Warehouse className="w-5 h-5" />
                  </div>
                  <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {farm.code}
                  </span>
                </div>

                <div>
                  <h3 className="text-base font-semibold text-slate-900">
                    {farm.name}
                  </h3>
                  <p className="text-xs text-slate-500 flex items-center gap-1 mt-1">
                    <MapPin className="w-3.5 h-3.5 text-slate-400" />
                    {farm.location}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-3 border-t border-slate-100 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                      Total Area
                    </span>
                    <span className="text-slate-800 font-bold text-sm">
                      {farm.total_area_ha} ha
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">
                      Fields
                    </span>
                    <span className="text-slate-800 font-bold text-sm">
                      {farm.active_fields_count} parcels
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Farm Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add Farm Estate"
        description="Register a new central farm estate inside your organization."
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleAddFarm}>
              Save Farm
            </Button>
          </>
        }
      >
        <form onSubmit={handleAddFarm} className="space-y-4">
          <Input
            label="Farm Name"
            placeholder="e.g. North Plain Agro"
            required
            value={newFarmName}
            onChange={(e) => setNewFarmName(e.target.value)}
          />
          <Input
            label="Location"
            placeholder="e.g. Mazowieckie, Poland"
            value={newFarmLocation}
            onChange={(e) => setNewFarmLocation(e.target.value)}
          />
          <Input
            label="Total Area (Hectares)"
            type="number"
            step="0.1"
            placeholder="e.g. 250.5"
            value={newFarmArea}
            onChange={(e) => setNewFarmArea(e.target.value)}
          />
        </form>
      </Modal>
    </div>
  );
};
