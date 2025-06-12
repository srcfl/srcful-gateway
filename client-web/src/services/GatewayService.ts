import {
  NetworkInfo,
  EnergyOverviewResponse,
  Device,
  DeviceMode,
} from "../types/api";

// Base configuration for the Gateway API
const API_BASE_URL = "/api";
const DEFAULT_TIMEOUT = 10000; // 10 seconds

// Custom error class for Gateway API errors
export class GatewayApiError extends Error {
  constructor(message: string, public status?: number, public response?: any) {
    super(message);
    this.name = "GatewayApiError";
  }
}

// Service class for Gateway API interactions
export class GatewayService {
  private static instance: GatewayService;
  private baseUrl: string;
  private timeout: number;

  private constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    this.timeout = DEFAULT_TIMEOUT;
  }

  // Singleton pattern to ensure single instance
  public static getInstance(): GatewayService {
    if (!GatewayService.instance) {
      GatewayService.instance = new GatewayService();
    }
    return GatewayService.instance;
  }

  // Generic fetch wrapper with error handling and timeout
  private async fetchWithTimeout<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    const requestOptions: RequestInit = {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    };

    try {
      const response = await fetch(`${this.baseUrl}${url}`, requestOptions);
      clearTimeout(timeoutId);

      if (!response.ok) {
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

        try {
          const errorData = await response.json();
          errorMessage = errorData.message || errorData.error || errorMessage;
        } catch {
          // If parsing JSON fails, use the default error message
        }

        throw new GatewayApiError(errorMessage, response.status, response);
      }

      const data = await response.json();
      return data;
    } catch (error: unknown) {
      clearTimeout(timeoutId);

      if (error instanceof GatewayApiError) {
        throw error;
      }

      if (error instanceof Error && error.name === "AbortError") {
        throw new GatewayApiError(
          "Request timeout - Gateway service not responding"
        );
      }

      throw new GatewayApiError(
        error instanceof Error ? error.message : "Unknown error occurred"
      );
    }
  }

  // Network related API calls
  public async getNetworkInfo(): Promise<NetworkInfo> {
    return this.fetchWithTimeout<NetworkInfo>("/network/address");
  }

  // Energy related API calls
  public async getEnergyOverview(): Promise<EnergyOverviewResponse> {
    return this.fetchWithTimeout<EnergyOverviewResponse>("/dee");
  }

  // Device related API calls
  public async getDevices(): Promise<Device[]> {
    return this.fetchWithTimeout<Device[]>("/device");
  }

  public async setDeviceMode(
    deviceSn: string,
    mode: DeviceMode
  ): Promise<void> {
    return this.fetchWithTimeout<void>(`/device/${deviceSn}/mode/${mode}`, {
      method: "POST",
    });
  }

  public async setBatteryPower(deviceSn: string, power: number): Promise<void> {
    return this.fetchWithTimeout<void>(
      `/device/${deviceSn}/battery/power/${power}`,
      {
        method: "POST",
      }
    );
  }

  public async setGridCurrentLimit(
    deviceSn: string,
    limit: number
  ): Promise<void> {
    return this.fetchWithTimeout<void>(
      `/device/${deviceSn}/grid/current/${limit}`,
      {
        method: "POST",
      }
    );
  }

  public async setGridPowerLimit(
    deviceSn: string,
    limit: number
  ): Promise<void> {
    return this.fetchWithTimeout<void>(
      `/device/${deviceSn}/grid/limit/${limit}`,
      {
        method: "POST",
      }
    );
  }

  public async setBatteryPowerLimit(
    deviceSn: string,
    limit: number
  ): Promise<void> {
    return this.fetchWithTimeout<void>(
      `/device/${deviceSn}/battery/limit/${limit}`,
      {
        method: "POST",
      }
    );
  }
}

// Export singleton instance for easy access
export const gatewayService = GatewayService.getInstance();

// Export default instance
export default gatewayService;
