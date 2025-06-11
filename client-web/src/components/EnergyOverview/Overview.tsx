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
import { EnergyOverviewResponse, EnergyOverviewSettings } from '../../types/api';

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
    net: number; // Positive = discharging, Negative = charging
    isActive: boolean;
    soc?: number;
    isCharging?: boolean;
    isDischarging?: boolean;
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

// Helper function to format power with appropriate unit
const formatPowerWithUnit = (kWValue: number): { value: number; unit: string } => {
  if (!kWValue) return { value: 0, unit: 'kW' };
  
  const absValue = Math.abs(kWValue);
  if (absValue < 1) {
    // Convert to watts for values under 1kW
    const watts = kWValue * 1000;
    return { 
      value: formatNumber(watts, 0), // No decimals for watts
      unit: 'W' 
    };
  } else {
    // Keep as kW for values 1kW and above
    const decimals = absValue >= 10 ? 1 : 2;
    return { 
      value: formatNumber(kWValue, decimals), 
      unit: 'kW' 
    };
  }
};

// Process DEE data into our energy structure
const processEnergyData = (deeData: EnergyOverviewResponse): EnergyData => {
  let solarPower = 0;
  let batteryPower = 0;
  let gridImport = 0;   // Power imported FROM grid (always positive)
  let gridExport = 0;   // Power exported TO grid (always positive)
  let batterySoC = 0;
  let batteryCount = 0;

  // Process DEE items
  deeData.data.dee.forEach(item => {
    // Sum solar power (always positive production)
    if (item.solar) {
      solarPower += item.solar.power;
    }

    // Sum battery power and extract status info
    if (item.battery) {
      batteryPower += item.battery.power;
      
      // Aggregate SoC (we'll average multiple batteries)
      if (item.battery.soc !== undefined) {
        batterySoC += item.battery.soc;
        batteryCount++;
      }
    }

    // Process meter data - handle grid import/export
    if (item.meter) {
      // Sungrow meter logic:
      // production > 0 = exporting to grid
      // production < 0 = importing from grid
      // consumption < 0 = importing from grid
      
      if (item.meter.production > 0) {
        gridExport += item.meter.production;
      }
      
      if (item.meter.production < 0) {
        gridImport += Math.abs(item.meter.production);
      }
      
      if (item.meter.consumption < 0) {
        gridImport += Math.abs(item.meter.consumption);
      }
    }
  });

  // Calculate average SoC for multiple batteries
  const averageSoC = batteryCount > 0 ? batterySoC / batteryCount : undefined;

  // Energy balance calculation:
  // Home Load = Solar Generation + Battery Discharge + Grid Import - Battery Charge - Grid Export
  // 
  // Battery power from backend:
  // Positive = discharging (power flowing OUT of battery)
  // Negative = charging (power flowing INTO battery)
  
  const batteryDischarge = batteryPower > 0 ? batteryPower : 0;  // Positive = discharging
  const batteryCharge = batteryPower < 0 ? Math.abs(batteryPower) : 0;  // Negative = charging
  
  const homeConsumption = solarPower + batteryDischarge + gridImport - batteryCharge - gridExport;
  
  // Calculate net grid flow (positive = export, negative = import)
  const netGridFlow = gridExport - gridImport;
  
  // Determine charging/discharging status based on power flow
  const isCharging = batteryPower < -50; // Negative power = charging (with 50W threshold)
  const isDischarging = batteryPower > 50; // Positive power = discharging (with 50W threshold)
  
  return {
    solar: {
      power: solarPower,
      isActive: true  // Always active
    },
    grid: {
      net: netGridFlow / 1000, // Convert to kW (positive = export, negative = import)
      isActive: true  // Always active
    },
    home: {
      consumption: homeConsumption / 1000 // Convert to kW
    },
    battery: {
      net: batteryPower / 1000, // Convert to kW (positive = discharging, negative = charging)
      isActive: true,  // Always active
      soc: averageSoC,
      isCharging: isCharging,
      isDischarging: isDischarging
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
  const [settings, setSettings] = useState<EnergyOverviewSettings | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEnergyData = async () => {
      try {
        const response = await gatewayService.getEnergyOverview();
        const processedData = processEnergyData(response);
        setEnergyData(processedData);
        setSettings(response.settings);
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
      
      {/* Power Limits Display */}
      {settings && (
        <div css={css`
          display: flex;
          justify-content: center;
          gap: 20px;
          margin-bottom: 15px;
          font-size: 11px;
        `}>
          <div css={css`
            background: rgba(42, 42, 64, 0.6);
            padding: 4px 8px;
            border-radius: 6px;
            border: 1px solid #666;
            color: #ccc;
          `}>
            <span css={css`color: #888; font-weight: 500;`}>Grid Limit: </span>
            <span css={css`color: #fff; font-weight: 600;`}>{(settings.grid_power_limit / 1000).toFixed(1)} kW</span>
          </div>
          <div css={css`
            background: rgba(42, 42, 64, 0.6);
            padding: 4px 8px;
            border-radius: 6px;
            border: 1px solid #6f42c1;
            color: #ccc;
          `}>
            <span css={css`color: #888; font-weight: 500;`}>Battery Limit: </span>
            <span css={css`color: #fff; font-weight: 600;`}>{(settings.battery_power_limit / 1000).toFixed(1)} kW</span>
          </div>
        </div>
      )}
      
      <div css={FlowWrapper}>
        {/* Solar Panel */}
        <div 
          css={[Circle, SolarCircle]} 
          className={energyData.solar.isActive ? '' : 'inactive'}
        >
          <PvIcon />
          <span>
            {energyData.solar.isActive ? (() => {
              const formatted = formatPowerWithUnit(wattToKW(energyData.solar.power));
              return formatted.value;
            })() : '-'}
            <span>{energyData.solar.isActive ? formatPowerWithUnit(wattToKW(energyData.solar.power)).unit : 'kW'}</span>
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
                {(() => {
                  const formatted = formatPowerWithUnit(Math.abs(energyData.grid.net));
                  return formatted.value;
                })()}
              </>
            )}
            {!energyData.grid.isActive && '-'}
            <span>{energyData.grid.isActive ? formatPowerWithUnit(Math.abs(energyData.grid.net)).unit : 'kW'}</span>
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
            {(() => {
              const formatted = formatPowerWithUnit(state.houseConsumption);
              return formatted.value;
            })()} 
            <span>{formatPowerWithUnit(state.houseConsumption).unit}</span>
          </span>
        </div>

        {/* Battery */}
        <div 
          css={[Circle, BatteryCircle]} 
          className={energyData.battery.isActive ? '' : 'inactive'}
        >
          {/* Power Arrow - Above battery icon */}
          <div css={css`margin-bottom: 4px;`}>
            {energyData.battery.isActive && (
              <>
                {energyData.battery.net > 0 ? (
                  <UilArrowUp style={ArrowColorStyle('#e69373')} />
                ) : energyData.battery.net < 0 ? (
                  <UilArrowDown style={ArrowColorStyle('lightblue')} />
                ) : null}
              </>
            )}
          </div>
          
          <BatteryIcon css={css`width: 70px!important;`} />
          <span>
            {energyData.battery.isActive && (
              <>
                {(() => {
                  const formatted = formatPowerWithUnit(Math.abs(energyData.battery.net));
                  return formatted.value;
                })()}
              </>
            )}
            {!energyData.battery.isActive && '-'}
            <span>{energyData.battery.isActive ? formatPowerWithUnit(Math.abs(energyData.battery.net)).unit : 'kW'}</span>
          </span>
          
          {/* SoC Display - Without "SoC" text */}
          {energyData.battery.soc !== undefined && (
            <span css={css`
              font-size: 12px;
              color: ${energyData.battery.soc < 20 ? '#f44336' : energyData.battery.soc < 50 ? '#FF9800' : '#4CAF50'};
              font-weight: 600;
              margin-top: 2px;
            `}>
              {Math.round(energyData.battery.soc)}%
            </span>
          )}
        </div>

        {/* Battery Status Display - Below the circle */}
        <div css={css`
          position: absolute;
          bottom: 10px;
          left: 180px;
          text-align: center;
          width: 140px;
        `}>
          <span css={css`
            font-size: 12px;
            color: ${energyData.battery.isCharging ? '#4CAF50' : energyData.battery.isDischarging ? '#f44336' : '#fff'} !important;
            font-weight: 500;
            text-transform: uppercase;
            display: block;
            text-align: center;
          `}>
            {energyData.battery.isCharging ? 'CHARGING' : energyData.battery.isDischarging ? 'DISCHARGING' : 'IDLE'}
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