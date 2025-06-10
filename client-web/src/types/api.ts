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
}

export interface BatteryData {
  power: number;
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

export interface EnergyOverviewResponse {
  status: string;
  data: EnergyOverviewData;
} 