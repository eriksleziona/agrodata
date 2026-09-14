export type UserRole = "OWNER" | "ADMIN" | "OPERATOR" | "FARMER" | "VIEWER";

export interface User {
  id: string;
  organization_id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  organization_id: string;
  email: string;
  password: string;
}

export interface RegisterRequest {
  organization_id: string;
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  role?: UserRole;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Machine {
  id: string;
  organization_id: string;
  name: string;
  manufacturer?: string | null;
  model?: string | null;
  serial_number?: string | null;
  year?: number | null;
  power_hp?: number | null;
  device_id?: string | null;
  created_at: string;
  updated_at: string;
}

export interface MachineCreate {
  organization_id: string;
  name: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  year?: number;
  power_hp?: number;
  device_id?: string;
}

export interface MachineUpdate {
  name?: string;
  manufacturer?: string;
  model?: string;
  serial_number?: string;
  year?: number;
  power_hp?: number;
  device_id?: string;
}

export type JobStatus =
  | "PLANNED"
  | "STARTED"
  | "PAUSED"
  | "COMPLETED"
  | "CANCELLED";

export interface Job {
  id: string;
  organization_id: string;
  farm_id?: string | null;
  field_id?: string | null;
  machine_id?: string | null;
  implement_id?: string | null;
  operator_id?: string | null;
  type: string;
  status: JobStatus;
  started_at?: string | null;
  finished_at?: string | null;
  area_planned?: number | null;
  area_completed: number;
  distance: number;
  working_time: number;
  idle_time: number;
  fuel_used: number;
  created_at: string;
  updated_at: string;
}

export interface JobCreate {
  organization_id: string;
  farm_id?: string;
  field_id?: string;
  machine_id?: string;
  implement_id?: string;
  operator_id?: string;
  type: string;
  area_planned?: number;
  status?: JobStatus;
}

export interface JobFinish {
  area_completed?: number;
  distance?: number;
  working_time?: number;
  idle_time?: number;
  fuel_used?: number;
}

export interface Farm {
  id: string;
  name: string;
  code: string;
  location: string;
  total_area_ha: number;
  active_fields_count: number;
  created_at: string;
}

export interface FieldItem {
  id: string;
  farm_id: string;
  farm_name: string;
  name: string;
  area_ha: number;
  crop_type: string;
  soil_type: string;
  status: "OPTIMAL" | "ATTENTION" | "DRY";
  created_at: string;
}
