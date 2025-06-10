import React, { useState, useEffect } from 'react';
import { Device, DeviceMode } from '../../types/api';
import { gatewayService } from '../../services/GatewayService';

const DeviceManager: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [processingDevice, setProcessingDevice] = useState<string | null>(null);
  const [deviceModes, setDeviceModes] = useState<Record<string, DeviceMode>>({});
  const [batteryPowers, setBatteryPowers] = useState<Record<string, string>>({});
  const [processingBattery, setProcessingBattery] = useState<string | null>(null);

  useEffect(() => {
    fetchDevices();
  }, []);

  const fetchDevices = async () => {
    try {
      setLoading(true);
      setError(null);
      const deviceList = await gatewayService.getDevices();
      setDevices(deviceList);
      
      // Initialize battery power inputs to 0 for new devices
      const newBatteryPowers: Record<string, string> = {};
      deviceList.forEach(device => {
        if (!batteryPowers[device.connection.sn]) {
          newBatteryPowers[device.connection.sn] = '0';
        }
      });
      setBatteryPowers(prev => ({ ...prev, ...newBatteryPowers }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch devices');
    } finally {
      setLoading(false);
    }
  };

  const handleSetDeviceMode = async (deviceSn: string, mode: DeviceMode) => {
    try {
      setProcessingDevice(deviceSn);
      await gatewayService.setDeviceMode(deviceSn, mode);
      
      // Update local mode tracking
      setDeviceModes(prev => ({ ...prev, [deviceSn]: mode }));
      
      // Optionally refresh devices list after successful mode change
      await fetchDevices();
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to set device mode to ${mode}`);
    } finally {
      setProcessingDevice(null);
    }
  };

  const handleBatteryPowerChange = (deviceSn: string, value: string) => {
    setBatteryPowers(prev => ({ ...prev, [deviceSn]: value }));
  };

  const handleSetBatteryPower = async (deviceSn: string) => {
    const powerStr = batteryPowers[deviceSn] || '0';
    const power = parseInt(powerStr, 10);
    
    if (isNaN(power)) {
      setError('Please enter a valid integer for battery power');
      return;
    }

    try {
      setProcessingBattery(deviceSn);
      await gatewayService.setBatteryPower(deviceSn, power);
      setError(null); // Clear any previous errors
    } catch (err) {
      setError(err instanceof Error ? err.message : `Failed to set battery power to ${power}W`);
    } finally {
      setProcessingBattery(null);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Device Manager</h2>
        <div className="flex items-center justify-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-300">Loading devices...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-semibold text-white mb-4">Device Manager</h2>
        <div className="bg-red-900/50 border border-red-500 rounded-lg p-4">
          <p className="text-red-200">Error: {error}</p>
          <button
            onClick={fetchDevices}
            className="mt-3 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-white">Device Manager</h2>
        <button
          onClick={fetchDevices}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
        >
          Refresh
        </button>
      </div>

      {devices.length === 0 ? (
        <div className="text-center py-8">
          <p className="text-gray-400">No devices found</p>
        </div>
      ) : (
        <div className="space-y-4">
          {devices.map((device) => (
            <div key={device.id} className="bg-gray-700 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div>
                  <h3 className="text-lg font-medium text-white">{device.name}</h3>
                  <p className="text-sm text-gray-400">{device.client_name}</p>
                </div>
                <div className="flex items-center space-x-2">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    device.is_open 
                      ? 'bg-green-900 text-green-200' 
                      : 'bg-red-900 text-red-200'
                  }`}>
                    {device.is_open ? 'Connected' : 'Disconnected'}
                  </span>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-3 mb-4 text-sm">
                <div>
                  <span className="text-gray-400">Device Type:</span>
                  <span className="ml-2 text-white">{device.connection.device_type}</span>
                </div>
                <div>
                  <span className="text-gray-400">Serial Number:</span>
                  <span className="ml-2 text-white">{device.connection.sn}</span>
                </div>
                <div>
                  <span className="text-gray-400">IP Address:</span>
                  <span className="ml-2 text-white">{device.connection.ip}:{device.connection.port}</span>
                </div>
                <div>
                  <span className="text-gray-400">Connection:</span>
                  <span className="ml-2 text-white">{device.connection.connection}</span>
                </div>
              </div>

              <div className="space-y-3">
                <div className="flex space-x-3">
                  <button
                    onClick={() => handleSetDeviceMode(device.connection.sn, 'control')}
                    disabled={processingDevice === device.connection.sn}
                    className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                      processingDevice === device.connection.sn
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : deviceModes[device.connection.sn] === 'control'
                        ? 'bg-orange-500 text-white'
                        : 'bg-orange-600 hover:bg-orange-700 text-white'
                    }`}
                  >
                    {processingDevice === device.connection.sn ? 'Processing...' : 'Control Mode'}
                  </button>
                  <button
                    onClick={() => handleSetDeviceMode(device.connection.sn, 'read')}
                    disabled={processingDevice === device.connection.sn}
                    className={`px-4 py-2 rounded-lg transition-colors font-medium ${
                      processingDevice === device.connection.sn
                        ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                        : deviceModes[device.connection.sn] === 'read'
                        ? 'bg-green-500 text-white'
                        : 'bg-green-600 hover:bg-green-700 text-white'
                    }`}
                  >
                    {processingDevice === device.connection.sn ? 'Processing...' : 'Read Mode'}
                  </button>
                </div>

                {/* Battery Power Control - Only show when in control mode */}
                {deviceModes[device.connection.sn] === 'control' && (
                  <div className="bg-gray-600 rounded-lg p-4 border-l-4 border-orange-500">
                    <h4 className="text-sm font-medium text-white mb-3">Battery Power Control</h4>
                    <div className="flex items-center space-x-3">
                      <div className="flex-1">
                        <input
                          type="number"
                          value={batteryPowers[device.connection.sn] || '0'}
                          onChange={(e) => handleBatteryPowerChange(device.connection.sn, e.target.value)}
                          placeholder="Power (W)"
                          className="w-full px-3 py-2 bg-gray-700 border border-gray-500 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                          disabled={processingBattery === device.connection.sn}
                        />
                        <p className="text-xs text-gray-400 mt-1">
                          Positive = Charging, Negative = Discharging
                        </p>
                      </div>
                      <button
                        onClick={() => handleSetBatteryPower(device.connection.sn)}
                        disabled={processingBattery === device.connection.sn}
                        className={`px-4 py-2 rounded-lg transition-colors font-medium whitespace-nowrap ${
                          processingBattery === device.connection.sn
                            ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700 text-white'
                        }`}
                      >
                        {processingBattery === device.connection.sn ? 'Setting...' : 'Set Power'}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default DeviceManager; 