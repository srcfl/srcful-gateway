// Network related types
export interface NetworkInfo {
  ip: string;
  port: number;
  eth0_mac: string;
  wlan0_mac: string;
  interfaces?: Record<string, string>;
}

// Energy related types
export interface MeterData {
  production: number;
  consumption: number;
  load_power: number;
}

export interface BatteryData {
  power: number;
  soc: number;
  is_charging: boolean;
  is_discharging: boolean;
}

export interface SolarData {
  power: number;
}

export interface DeeItem {
  meter?: MeterData;
  battery?: BatteryData;
  solar?: SolarData;
}

export interface EnergyOverviewData {
  dee: DeeItem[];
}

export interface EnergyOverviewSettings {
  grid_power_limit: number;
  battery_power_limit: number;
}

export interface EnergyOverviewResponse {
  status: string;
  settings: EnergyOverviewSettings;
  data: EnergyOverviewData;
}

// Device related types
export interface DeviceConnection {
  device_type: string;
  slave_id: number;
  sn: string;
  connection: string;
  ip: string;
  port: number;
  mac: string;
}

export interface Device {
  connection: DeviceConnection;
  is_open: boolean;
  id: string;
  name: string;
  client_name: string;
}

export type DeviceMode = "control" | "read";
