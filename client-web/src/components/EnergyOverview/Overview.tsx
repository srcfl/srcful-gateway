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
    net: number; // Positive = export, Negative = import
    isActive: boolean;
  };
  home: {
    consumption: number;
  };
  battery: {
    net: number; // Positive = charging, Negative = discharging
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
  let gridProduction = 0;  // Export TO grid
  let gridConsumption = 0; // Import FROM grid

  // Process DEE items
  deeData.data.dee.forEach(item => {
    // Sum solar power (always positive production)
    if (item.solar) {
      solarPower += item.solar.power;
    }

    // Sum battery power (positive = charging/consuming, negative = discharging/producing)
    if (item.battery) {
      batteryPower += item.battery.power;
    }

    // Sum meter data (absolute values)
    if (item.meter) {
      gridProduction += item.meter.production;   // Export to grid
      gridConsumption += item.meter.consumption; // Import from grid
    }
  });

  // Calculate home consumption using energy balance:
  // Energy Sources = Energy Consumers
  // Solar + Battery_discharge + Grid_import = Home + Battery_charging + Grid_export
  // Therefore: Home = Solar + Battery_discharge + Grid_import - Battery_charging - Grid_export
  
  const batteryDischarge = batteryPower < 0 ? Math.abs(batteryPower) : 0;
  const batteryCharging = batteryPower > 0 ? batteryPower : 0;
  
  const homeConsumption = solarPower + batteryDischarge + gridConsumption - batteryCharging - gridProduction;
  
  // Calculate net grid flow (positive = export, negative = import)
  const netGridFlow = gridProduction - gridConsumption;
  
  return {
    solar: {
      power: solarPower,
      isActive: solarPower > 0
    },
    grid: {
      net: netGridFlow / 1000, // Convert to kW (positive = export, negative = import)
      isActive: netGridFlow !== 0
    },
    home: {
      consumption: homeConsumption / 1000 // Convert to kW
    },
    battery: {
      net: batteryPower / 1000, // Convert to kW (positive = charging, negative = discharging)
      isActive: batteryPower !== 0
    }
  };
};

const getSystemState = (energyData: EnergyData) => {
  const solarKw = wattToKW(energyData.solar.power);
  const gridNet = energyData.grid.net; // Positive = export, Negative = import
  
  // Calculate energy flows
  const isExportingSolarToGrid = solarKw > 0 && gridNet > 0;
  const isExportingSolarToHouse = solarKw > 0 && energyData.home.consumption > 0;
  const isImportingGridToHouse = gridNet < 0;
  
  return {
    isExportingSolarToGrid,
    isExportingSolarToHouse,
    isImportingGridToHouse,
    isExportingSolarToBattery: solarKw > 0 && energyData.battery.net > 0,
    isExportingBatteryToGrid: energyData.battery.net < 0 && gridNet > 0,
    isExportingBatteryToHouse: energyData.battery.net < 0 && energyData.home.consumption > 0,
    isImportingGridToBattery: energyData.battery.net > 0 && gridNet < 0,
    houseConsumption: energyData.home.consumption
  };
};

const ArrowColorStyle = (color: string): React.CSSProperties => ({
  stroke: color,
  fill: color,
  color: color
});

const Curve: React.FC<{ className: string; animate?: boolean; reverse?: boolean }> = ({ className, animate, reverse }) => {
  const pathData = reverse ? "M49 49 Q 1 49 1 1" : "M1 1 Q 1 49 49 49";
  
  return (
    <svg 
      className={`curve ${className} ${animate ? 'animate-particle' : ''}`} 
      css={CurveStyle} 
      viewBox="0 0 50 50"
    >
      <path d={pathData}/>
      {animate && <path className="particle" d={pathData}/>}
    </svg>
  );
};

const Line: React.FC<{ className: string; animate?: boolean; reverse?: boolean }> = ({ className, animate, reverse }) => {
  const x1 = reverse ? "180" : "20";
  const x2 = reverse ? "20" : "180";
  
  return (
    <svg 
      className={`line ${className} ${animate ? 'animate-particle' : ''}`} 
      css={LineStyle} 
      viewBox="15 45 170 10"
    >
      <line x1={x1} y1="50" x2={x2} y2="50"/>
      {animate && <line className="particle" x1={x1} y1="50" x2={x2} y2="50"/>}
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
          reverse={true}
        />
        <Curve 
          className="export-solar-to-house" 
          animate={state.isExportingSolarToHouse} 
        />
        <Line 
          className="export-solar-to-battery" 
          animate={state.isExportingSolarToBattery} 
        />

        {/* Grid */}
        <div 
          css={[Circle, GridCircle]} 
          className={energyData.grid.isActive ? '' : 'inactive'}
        >
          <GridIcon />
          <span>
            {energyData.grid.isActive && (
              <>
                {energyData.grid.net > 0 ? (
                  <UilArrowLeft style={ArrowColorStyle('lightblue')} />
                ) : (
                  <UilArrowRight style={ArrowColorStyle('#e69373')} />
                )}
                {formatNumber(Math.abs(energyData.grid.net))}
              </>
            )}
            {!energyData.grid.isActive && '-'}
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
          <span>
            {energyData.battery.isActive && (
              <>
                {energyData.battery.net > 0 ? (
                  <UilArrowDown style={ArrowColorStyle('lightblue')} />
                ) : (
                  <UilArrowUp style={ArrowColorStyle('#e69373')} />
                )}
                {formatNumber(Math.abs(energyData.battery.net))}
              </>
            )}
            {!energyData.battery.isActive && '-'}
            <span>kW</span>
          </span>
        </div>

        <Curve 
          className="import-export-battery-to-grid" 
          animate={state.isExportingBatteryToGrid || state.isImportingGridToBattery}
          reverse={state.isImportingGridToBattery}
        />
        <Curve 
          className="export-battery-to-house" 
          animate={state.isExportingBatteryToHouse}
          reverse={true}
        />
      </div>
    </div>
  );
};

export default Overview; 