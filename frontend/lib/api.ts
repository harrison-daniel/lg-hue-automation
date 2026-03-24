const API_BASE = "/api";

// --- Device types ---

export interface DeviceStatus {
  name: string;
  type: "tv" | "hue";
  online: boolean;
  state: string;
  entity_id: string;
}

export interface DevicesResponse {
  devices: DeviceStatus[];
}

// --- Scene types ---

export interface SceneAction {
  type: string;
  target: string;
  description: string;
}

export interface SceneDefinition {
  name: string;
  display_name: string;
  description: string;
  icon: string;
  time_of_day: "day" | "night" | "any";
  actions: SceneAction[];
}

export interface ScenesListResponse {
  scenes: SceneDefinition[];
}

export interface SceneActivateResponse {
  scene: string;
  success: boolean;
  message: string;
  errors: string[];
}

// --- Diagnostics types ---

export interface CpuTemperature {
  label: string;
  current: number;
  high: number | null;
  critical: number | null;
}

export interface DiskUsage {
  total_gb: number;
  used_gb: number;
  free_gb: number;
  percent: number;
}

export interface MemoryUsage {
  total_gb: number;
  used_gb: number;
  available_gb: number;
  percent: number;
}

export interface DiagnosticsResponse {
  cpu_temps: CpuTemperature[];
  disk: DiskUsage;
  memory: MemoryUsage;
  cpu_percent: number;
  uptime_seconds: number;
  uptime_human: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  ha_connected: boolean;
}

// --- API functions ---

export async function getScenes(): Promise<ScenesListResponse> {
  const res = await fetch(`${API_BASE}/scenes`);
  if (!res.ok) throw new Error(`Failed to fetch scenes: ${res.status}`);
  return res.json();
}

export async function activateScene(
  name: string
): Promise<SceneActivateResponse> {
  const res = await fetch(`${API_BASE}/scenes/${name}/activate`, {
    method: "POST",
  });
  if (!res.ok) throw new Error(`Failed to activate scene: ${res.status}`);
  return res.json();
}

export async function getDeviceStatus(): Promise<DevicesResponse> {
  const res = await fetch(`${API_BASE}/devices/status`);
  if (!res.ok) throw new Error(`Failed to fetch device status: ${res.status}`);
  return res.json();
}

export async function getDiagnostics(): Promise<DiagnosticsResponse> {
  const res = await fetch(`${API_BASE}/diagnostics`);
  if (!res.ok) throw new Error(`Failed to fetch diagnostics: ${res.status}`);
  return res.json();
}

export async function getHealth(): Promise<HealthResponse> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
  return res.json();
}
