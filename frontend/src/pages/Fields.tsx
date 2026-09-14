import React, { useState } from "react";
import { Grid3X3, Plus, Search } from "lucide-react";
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
import { EmptyState } from "../components/ui/EmptyState";
import { Modal } from "../components/ui/Modal";
import { FieldItem } from "../api/types";

const mockFields: FieldItem[] = [
  {
    id: "1",
    farm_id: "1",
    farm_name: "Green Valley Agriculture",
    name: "North Ridge Parcel A1",
    area_ha: 45.2,
    crop_type: "Winter Wheat",
    soil_type: "Loam / Chernozem",
    status: "OPTIMAL",
    created_at: "2026-03-01T10:00:00Z",
  },
  {
    id: "2",
    farm_id: "1",
    farm_name: "Green Valley Agriculture",
    name: "East Meadow B2",
    area_ha: 68.0,
    crop_type: "Rapeseed",
    soil_type: "Sandy Clay",
    status: "OPTIMAL",
    created_at: "2026-03-05T11:00:00Z",
  },
  {
    id: "3",
    farm_id: "2",
    farm_name: "Baltic Harvest Estates",
    name: "Coastal Lowland C4",
    area_ha: 112.5,
    crop_type: "Corn / Maize",
    soil_type: "Alluvial Silt",
    status: "ATTENTION",
    created_at: "2026-03-12T09:30:00Z",
  },
  {
    id: "4",
    farm_id: "2",
    farm_name: "Baltic Harvest Estates",
    name: "Southern Plateau D1",
    area_ha: 89.4,
    crop_type: "Barley",
    soil_type: "Clay Loam",
    status: "DRY",
    created_at: "2026-03-20T14:15:00Z",
  },
];

const statusStyles: Record<
  FieldItem["status"],
  { label: string; bg: string; text: string }
> = {
  OPTIMAL: {
    label: "Optimal Moisture",
    bg: "bg-emerald-50 border-emerald-200",
    text: "text-emerald-700",
  },
  ATTENTION: {
    label: "Check Nitrogen",
    bg: "bg-amber-50 border-amber-200",
    text: "text-amber-700",
  },
  DRY: {
    label: "Low Moisture",
    bg: "bg-red-50 border-red-200",
    text: "text-red-700",
  },
};

export const Fields: React.FC = () => {
  const [fields, setFields] = useState<FieldItem[]>(mockFields);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Form state
  const [name, setName] = useState("");
  const [farmName, setFarmName] = useState("");
  const [areaHa, setAreaHa] = useState("");
  const [cropType, setCropType] = useState("Winter Wheat");
  const [soilType, setSoilType] = useState("Loam");

  const filteredFields = fields.filter(
    (f) =>
      f.name.toLowerCase().includes(search.toLowerCase()) ||
      f.farm_name.toLowerCase().includes(search.toLowerCase()) ||
      f.crop_type.toLowerCase().includes(search.toLowerCase()),
  );

  const handleAddField = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !areaHa) return;

    const newField: FieldItem = {
      id: String(Date.now()),
      farm_id: "1",
      farm_name: farmName || "Main Farm Estate",
      name,
      area_ha: parseFloat(areaHa),
      crop_type: cropType,
      soil_type: soilType,
      status: "OPTIMAL",
      created_at: new Date().toISOString(),
    };

    setFields([newField, ...fields]);
    setIsModalOpen(false);
    setName("");
    setFarmName("");
    setAreaHa("");
  };

  const totalManagedHa = fields.reduce((acc, f) => acc + f.area_ha, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Agricultural Fields
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Parcel catalog, crop allocation, and soil metrics (
            {totalManagedHa.toFixed(1)} ha under management).
          </p>
        </div>
        <Button
          variant="primary"
          size="sm"
          onClick={() => setIsModalOpen(true)}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          Add Field Parcel
        </Button>
      </div>

      {/* Filter Bar */}
      <div className="flex items-center gap-3">
        <div className="max-w-md w-full">
          <Input
            placeholder="Search fields by name, farm estate, or crop..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            leftIcon={<Search className="w-4 h-4" />}
          />
        </div>
      </div>

      {/* Fields Table */}
      {filteredFields.length === 0 ? (
        <EmptyState
          icon={<Grid3X3 className="w-8 h-8" />}
          title="No field parcels found"
          description={
            search
              ? "No fields matched your filter criteria."
              : "Add your agricultural field parcels to begin tracking operations."
          }
          actionText="Add Field Parcel"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Parcel Name</TableHead>
              <TableHead>Farm Estate</TableHead>
              <TableHead>Area (Hectares)</TableHead>
              <TableHead>Active Crop</TableHead>
              <TableHead>Soil Classification</TableHead>
              <TableHead>Condition</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredFields.map((field) => {
              const status = statusStyles[field.status];
              return (
                <TableRow key={field.id}>
                  <TableCell className="font-semibold text-slate-900">
                    {field.name}
                  </TableCell>
                  <TableCell className="text-slate-600">
                    {field.farm_name}
                  </TableCell>
                  <TableCell className="font-mono text-slate-800 font-medium">
                    {field.area_ha.toFixed(1)} ha
                  </TableCell>
                  <TableCell>
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-agro-50 text-agro-800 border border-agro-200">
                      {field.crop_type}
                    </span>
                  </TableCell>
                  <TableCell className="text-slate-500 text-xs">
                    {field.soil_type}
                  </TableCell>
                  <TableCell>
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-semibold border ${status.bg} ${status.text}`}
                    >
                      {status.label}
                    </span>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      )}

      {/* Add Field Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add Field Parcel"
        description="Register a parcel of arable land with initial soil & crop settings."
        footer={
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsModalOpen(false)}
            >
              Cancel
            </Button>
            <Button variant="primary" size="sm" onClick={handleAddField}>
              Save Parcel
            </Button>
          </>
        }
      >
        <form onSubmit={handleAddField} className="space-y-4">
          <Input
            label="Field Parcel Name"
            placeholder="e.g. West Meadow A3"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            label="Belongs to Farm"
            placeholder="e.g. Green Valley Agriculture"
            value={farmName}
            onChange={(e) => setFarmName(e.target.value)}
          />
          <Input
            label="Area (Hectares)"
            type="number"
            step="0.1"
            placeholder="e.g. 54.2"
            required
            value={areaHa}
            onChange={(e) => setAreaHa(e.target.value)}
          />
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Crop Type"
              placeholder="e.g. Winter Wheat"
              value={cropType}
              onChange={(e) => setCropType(e.target.value)}
            />
            <Input
              label="Soil Classification"
              placeholder="e.g. Loam / Clay"
              value={soilType}
              onChange={(e) => setSoilType(e.target.value)}
            />
          </div>
        </form>
      </Modal>
    </div>
  );
};
