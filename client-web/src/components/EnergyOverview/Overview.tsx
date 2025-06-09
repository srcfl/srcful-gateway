/** @jsxImportSource @emotion/react */
import React, { useState, useEffect } from 'react';
import { 
  BatteryCircle, 
  Circle, 
  GridCircle, 
  HomeCircle, 
  OverviewWrapperStyle, 
  SolarCircle, 
  CurveStyle, 
  LineStyle, 
  FlowWrapper 
} from './Overview.css';
import PvIcon from '../Icons/PvIcon';
import BatteryIcon from '../Icons/BatteryIcon';
import HomeIcon from '../Icons/HomeIcon';
import GridIcon from '../Icons/GridIcon';
import { 
  UilArrowDown, 
  UilArrowUp, 
  UilArrowLeft, 
  UilArrowRight 
} from '../Icons/ArrowIcons';
import { css } from '@emotion/react';
import { gatewayService, GatewayApiError } from '../../services/GatewayService';
import { EnergyOverviewResponse } from '../../types/api';

// Energy data structure
interface EnergyData {
  solar: {
    power: number;
    isActive: boolean;
  };
  grid: {
    import: number;
    export: number;
    isActive: boolean;
  };
  home: {
    consumption: number;
  };
  battery: {
    charging: number;
    discharging: number;
    isActive: boolean;
  };
}

const formatNumber = (number: number, decimals: number = 2): number => {
  if (!number) return 0;
  return Number(number.toFixed(decimals));
};

const wattToKW = (watt: number): number => {
  if (!watt) return 0;
  const kW = watt / 1000;
  
  // Use 1 decimal if over 9, otherwise use 2 decimals
  const decimals = kW >= 10 ? 1 : 2;
  return formatNumber(kW, decimals);
};

// Process DEE data into our energy structure
const processEnergyData = (deeData: EnergyOverviewResponse): EnergyData => {
  let solarPower = 0;
  let batteryPower = 0;
  let meterProduction = 0;
  let meterConsumption = 0;

  // Process DEE items
  deeData.data.dee.forEach(item => {
    // Sum solar power
    if (item.solar) {
      solarPower += item.solar.power;
    }

    // Sum battery power (negative = discharge, positive = charge)
    if (item.battery) {
      batteryPower += item.battery.power;
    }

    // Use first meter data found
    if (item.meter && meterProduction === 0 && meterConsumption === 0) {
      meterProduction = item.meter.production;
      meterConsumption = item.meter.consumption;
    }
  });

  // Calculate grid import/export based on energy balance
  // Total production = solar + battery discharge (if negative)
  const totalProduction = solarPower + (batteryPower < 0 ? Math.abs(batteryPower) : 0);
  // Total consumption = home consumption + battery charging (if positive)
  const totalConsumption = meterConsumption + (batteryPower > 0 ? batteryPower : 0);
  
  const energyBalance = totalProduction - totalConsumption;
  
  return {
    solar: {
      power: solarPower,
      isActive: solarPower > 0
    },
    grid: {
      import: energyBalance < 0 ? Math.abs(energyBalance) / 1000 : 0, // Convert to kW
      export: energyBalance > 0 ? energyBalance / 1000 : 0, // Convert to kW
      isActive: Math.abs(energyBalance) > 0
    },
    home: {
      consumption: meterConsumption / 1000 // Convert to kW
    },
    battery: {
      charging: batteryPower > 0 ? batteryPower / 1000 : 0, // Convert to kW
      discharging: batteryPower < 0 ? Math.abs(batteryPower) / 1000 : 0, // Convert to kW
      isActive: batteryPower !== 0
    }
  };
};

const getSystemState = (energyData: EnergyData) => {
  const solarKw = wattToKW(energyData.solar.power);
  const gridExport = energyData.grid.export;
  const gridImport = energyData.grid.import;
  
  // Calculate energy flows
  const isExportingSolarToGrid = solarKw > 0 && gridExport > 0;
  const isExportingSolarToHouse = solarKw > 0 && (solarKw - gridExport) > 0;
  const isImportingGridToHouse = gridImport > 0;
  
  return {
    isExportingSolarToGrid,
    isExportingSolarToHouse,
    isImportingGridToHouse,
    houseConsumption: energyData.home.consumption
  };
};

const ArrowColorStyle = (color: string): React.CSSProperties => ({
  stroke: color,
  fill: color,
  color: color
});

const Curve: React.FC<{ className: string; animate?: boolean }> = ({ className, animate }) => {
  return (
    <svg 
      className={`curve ${className} ${animate ? 'animate-particle' : ''}`} 
      css={CurveStyle} 
      viewBox="0 0 50 50"
    >
      <path d="M1 1 Q 1 49 49 49"/>
      {animate && <path className="particle" d="M1 1 Q 1 49 49 49"/>}
    </svg>
  );
};

const Line: React.FC<{ className: string; animate?: boolean }> = ({ className, animate }) => {
  return (
    <svg 
      className={`line ${className}`} 
      css={LineStyle} 
      viewBox="15 45 170 10"
    >
      <line x1="20" y1="50" x2="180" y2="50"/>
      {animate && <line className="particle" x1="20" y1="50" x2="180" y2="50"/>}
    </svg>
  );
};

const Overview: React.FC = () => {
  const [energyData, setEnergyData] = useState<EnergyData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEnergyData = async () => {
      try {
        const response = await gatewayService.getEnergyOverview();
        const processedData = processEnergyData(response);
        setEnergyData(processedData);
        setLoading(false);
      } catch (err) {
        if (err instanceof GatewayApiError) {
          setError(err.message);
        } else {
          setError('Failed to fetch energy data');
        }
        setLoading(false);
      }
    };

    fetchEnergyData();
    
    // Refresh data every 5 seconds
    const interval = setInterval(fetchEnergyData, 5000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div css={OverviewWrapperStyle}>
        <h2>Energy System Overview</h2>
        <p>Loading energy data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div css={OverviewWrapperStyle}>
        <h2>Energy System Overview</h2>
        <p style={{color: 'red'}}>Error: {error}</p>
      </div>
    );
  }

  if (!energyData) {
    return (
      <div css={OverviewWrapperStyle}>
        <h2>Energy System Overview</h2>
        <p>No energy data available</p>
      </div>
    );
  }

  const state = getSystemState(energyData);

  return (
    <div css={OverviewWrapperStyle}>
      <h2>Energy System Overview</h2>
      <p>Real-time energy flow visualization</p>
      <div css={FlowWrapper}>
        {/* Solar Panel */}
        <div 
          css={[Circle, SolarCircle]} 
          className={energyData.solar.isActive ? '' : 'inactive'}
        >
          <PvIcon />
          <span>
            {energyData.solar.isActive ? wattToKW(energyData.solar.power) : '-'}
            <span>kW</span>
          </span>
        </div>

        {/* Energy Flow Lines */}
        <Curve 
          className="export-solar-to-grid" 
          animate={state.isExportingSolarToGrid} 
        />
        <Curve 
          className="export-solar-to-house" 
          animate={state.isExportingSolarToHouse} 
        />
        <Line className="export-solar-to-battery" />

        {/* Grid */}
        <div 
          css={[Circle, GridCircle]} 
          className={energyData.grid.isActive ? '' : 'inactive'}
        >
          <GridIcon />
          <span className="in">
            <UilArrowLeft style={ArrowColorStyle('lightblue')} /> 
            {energyData.grid.isActive ? formatNumber(energyData.grid.export) : '-'} 
            <span>kW</span>
          </span>
          <span className="out">
            <UilArrowRight style={ArrowColorStyle('#e69373')} /> 
            {energyData.grid.isActive ? formatNumber(energyData.grid.import) : '-'} 
            <span>kW</span>
          </span>
        </div>

        <Line 
          className="import-grid-to-house" 
          animate={state.isImportingGridToHouse} 
        />

        {/* Home */}
        <div css={[Circle, HomeCircle]}>
          <HomeIcon />
          <span>
            {formatNumber(state.houseConsumption)} 
            <span>kW</span>
          </span>
        </div>

        {/* Battery */}
        <div 
          css={[Circle, BatteryCircle]} 
          className={energyData.battery.isActive ? '' : 'inactive'}
        >
          <BatteryIcon css={css`width: 70px!important;`} />
          <span className="in">
            <UilArrowDown style={ArrowColorStyle('lightblue')} />
            {energyData.battery.isActive ? formatNumber(energyData.battery.charging) : '-'} 
            <span>kW</span>
          </span>
          <span className="out">
            <UilArrowUp style={ArrowColorStyle('#e69373')} />
            {energyData.battery.isActive ? formatNumber(energyData.battery.discharging) : '-'} 
            <span>kW</span>
          </span>
        </div>

        <Curve className="import-export-battery-to-grid" />
        <Curve className="export-battery-to-house" />
      </div>
    </div>
  );
};

export default Overview; 