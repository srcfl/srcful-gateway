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
    load_power: number;
  };
  battery: {
    net: number; // Positive = discharging, Negative = charging
    isActive: boolean;
    soc?: number;
    isCharging?: boolean;
    isDischarging?: boolean;
  };
}

// Historical data point structure
interface GridDataPoint {
  timestamp: number;
  power: number; // Grid power in kW
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
  let loadPower = 0;
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
      loadPower = item.meter.load_power;
      
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
  
  // Positive = charging, negative = discharging
  const batteryDischarge = batteryPower < 0 ? Math.abs(batteryPower) : 0;  
  const batteryCharge = batteryPower > 0 ? batteryPower : 0;  
  
  const homeConsumption = loadPower;
  
  // Calculate net grid flow (positive = export, negative = import)
  const netGridFlow = gridExport - gridImport;
  
     // Determine charging/discharging status based on power flow
   const isCharging = batteryPower > 50; // Positive power = charging (with 50W threshold)
   const isDischarging = batteryPower < -50; // Negative power = discharging (with 50W threshold)
  
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
      load_power: homeConsumption / 1000 // Convert to kW
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
  const isExportingSolarToHouse = solarKw > 0 && energyData.home.load_power > 0;
  const isImportingGridToHouse = gridNet < 0;
  
  
  return {
    isExportingSolarToGrid,
    isExportingSolarToHouse,
    isImportingGridToHouse,
    isExportingSolarToBattery: solarKw > 0 && energyData.battery.net > 0,
    isExportingBatteryToGrid: energyData.battery.net < 0 && gridNet > 0,
    isExportingBatteryToHouse: energyData.battery.net < 0 && energyData.home.load_power > 0,
    isImportingGridToBattery: energyData.battery.net > 0 && gridNet < 0,
    houseConsumption: energyData.home.load_power
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

// Time frame options
const TIME_FRAMES = [
  { label: '30s', value: 30 * 1000 },
  { label: '1m', value: 60 * 1000 },
  { label: '5m', value: 5 * 60 * 1000 },
  { label: '10m', value: 10 * 60 * 1000 },
  { label: '15m', value: 15 * 60 * 1000 },
  { label: '20m', value: 20 * 60 * 1000 },
];

// Grid Power Chart Component
const GridPowerChart: React.FC<{ 
  data: GridDataPoint[], 
  gridLimit: number,
  selectedTimeFrame: number,
  onTimeFrameChange: (timeFrame: number) => void
}> = ({ data, gridLimit, selectedTimeFrame, onTimeFrameChange }) => {
  const chartWidth = 650;
  const chartHeight = 200;
  const padding = { top: 20, right: 30, bottom: 30, left: 50 };
  const plotWidth = chartWidth - padding.left - padding.right;
  const plotHeight = chartHeight - padding.top - padding.bottom;

  // Filter data for selected time frame
  const now = Date.now();
  const startTime = now - selectedTimeFrame;
  const filteredData = data.filter(point => point.timestamp >= startTime);

  if (!filteredData.length) {
    return (
      <div css={css`
        background: rgba(42, 42, 64, 0.3);
        border-radius: 8px;
        border: 1px solid #666;
        padding: 10px;
      `}>
        {/* Time Frame Selector */}
        <div css={css`
          display: flex;
          justify-content: center;
          gap: 5px;
          margin-bottom: 10px;
        `}>
          {TIME_FRAMES.map(({ label, value }) => (
            <button
              key={value}
              onClick={() => onTimeFrameChange(value)}
              css={css`
                padding: 4px 8px;
                font-size: 11px;
                border: 1px solid ${selectedTimeFrame === value ? '#4CAF50' : '#666'};
                background: ${selectedTimeFrame === value ? 'rgba(76, 175, 80, 0.2)' : 'rgba(42, 42, 64, 0.6)'};
                color: ${selectedTimeFrame === value ? '#4CAF50' : '#ccc'};
                border-radius: 4px;
                cursor: pointer;
                transition: all 0.2s;
                
                &:hover {
                  background: ${selectedTimeFrame === value ? 'rgba(76, 175, 80, 0.3)' : 'rgba(66, 66, 84, 0.8)'};
                }
              `}
            >
              {label}
            </button>
          ))}
        </div>
        
        <div css={css`
          width: ${chartWidth}px;
          height: ${chartHeight}px;
          display: flex;
          align-items: center;
          justify-content: center;
          color: #888;
          font-size: 14px;
        `}>
          Collecting data...
        </div>
      </div>
    );
  }

  // Find min/max values for scaling
  const maxAbsPower = Math.max(
    Math.abs(Math.min(...filteredData.map(d => d.power))),
    Math.abs(Math.max(...filteredData.map(d => d.power))),
    gridLimit / 1000 // Include grid limit in scaling
  );
  const yRange = maxAbsPower * 1.2; // Add 20% padding

  // Scale functions
  const scaleX = (timestamp: number) => {
    const relativeTime = timestamp - startTime;
    return padding.left + (relativeTime / selectedTimeFrame) * plotWidth;
  };

  const scaleY = (power: number) => {
    return padding.top + plotHeight / 2 - (power / yRange) * (plotHeight / 2);
  };

  // Create path for the line chart
  const pathData = filteredData
    .map((point, index) => {
      const x = scaleX(point.timestamp);
      const y = scaleY(point.power);
      return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
    })
    .join(' ');

  // Grid limit line positions
  const gridLimitKW = gridLimit / 1000;
  const gridLimitYPos = scaleY(gridLimitKW);
  const gridLimitYNeg = scaleY(-gridLimitKW);

  // Format time label based on selected timeframe
  const getTimeLabel = () => {
    const timeFrame = TIME_FRAMES.find(tf => tf.value === selectedTimeFrame);
    return `Time (${timeFrame?.label} window)`;
  };

  return (
    <div css={css`
      background: rgba(42, 42, 64, 0.3);
      border-radius: 8px;
      border: 1px solid #666;
      padding: 10px;
    `}>
      {/* Time Frame Selector */}
      <div css={css`
        display: flex;
        justify-content: center;
        gap: 5px;
        margin-bottom: 10px;
      `}>
        {TIME_FRAMES.map(({ label, value }) => (
          <button
            key={value}
            onClick={() => onTimeFrameChange(value)}
            css={css`
              padding: 4px 8px;
              font-size: 11px;
              border: 1px solid ${selectedTimeFrame === value ? '#4CAF50' : '#666'};
              background: ${selectedTimeFrame === value ? 'rgba(76, 175, 80, 0.2)' : 'rgba(42, 42, 64, 0.6)'};
              color: ${selectedTimeFrame === value ? '#4CAF50' : '#ccc'};
              border-radius: 4px;
              cursor: pointer;
              transition: all 0.2s;
              
              &:hover {
                background: ${selectedTimeFrame === value ? 'rgba(76, 175, 80, 0.3)' : 'rgba(66, 66, 84, 0.8)'};
              }
            `}
          >
            {label}
          </button>
        ))}
      </div>

      <h3 css={css`
        margin: 0 0 10px 0;
        font-size: 14px;
        color: #fff;
        text-align: center;
      `}>
        Grid Power ({TIME_FRAMES.find(tf => tf.value === selectedTimeFrame)?.label})
      </h3>
      
      <svg width={chartWidth} height={chartHeight}>
        {/* Background grid */}
        <defs>
          <pattern id="grid" width="40" height="30" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 30" fill="none" stroke="#333" strokeWidth="1" opacity="0.3"/>
          </pattern>
        </defs>
        <rect width={chartWidth} height={chartHeight} fill="url(#grid)"/>
        
        {/* Zero line */}
        <line 
          x1={padding.left} 
          y1={scaleY(0)} 
          x2={chartWidth - padding.right} 
          y2={scaleY(0)} 
          stroke="#666" 
          strokeWidth="2"
          strokeDasharray="5,5"
        />
        
        {/* Grid limit lines */}
        <line 
          x1={padding.left} 
          y1={gridLimitYPos} 
          x2={chartWidth - padding.right} 
          y2={gridLimitYPos} 
          stroke="#ff6b6b" 
          strokeWidth="2"
          strokeDasharray="3,3"
        />
        <line 
          x1={padding.left} 
          y1={gridLimitYNeg} 
          x2={chartWidth - padding.right} 
          y2={gridLimitYNeg} 
          stroke="#ff6b6b" 
          strokeWidth="2"
          strokeDasharray="3,3"
        />
        
        {/* Data line */}
        {pathData && (
          <path 
            d={pathData} 
            fill="none" 
            stroke="#4CAF50" 
            strokeWidth="2"
          />
        )}
        
        {/* Data points */}
        {filteredData.map((point, index) => (
          <circle
            key={index}
            cx={scaleX(point.timestamp)}
            cy={scaleY(point.power)}
            r="2"
            fill={point.power > 0 ? "#4CAF50" : "#f44336"}
          />
        ))}
        
        {/* Y-axis labels */}
        <text x={padding.left - 10} y={gridLimitYPos + 5} textAnchor="end" fontSize="10" fill="#ff6b6b">
          +{gridLimitKW.toFixed(1)}
        </text>
        <text x={padding.left - 10} y={scaleY(0) + 5} textAnchor="end" fontSize="10" fill="#666">
          0
        </text>
        <text x={padding.left - 10} y={gridLimitYNeg + 5} textAnchor="end" fontSize="10" fill="#ff6b6b">
          -{gridLimitKW.toFixed(1)}
        </text>
        
        {/* X-axis label */}
        <text x={chartWidth / 2} y={chartHeight - 5} textAnchor="middle" fontSize="10" fill="#888">
          {getTimeLabel()}
        </text>
        
        {/* Y-axis label */}
        <text x={15} y={chartHeight / 2} textAnchor="middle" fontSize="10" fill="#888" transform={`rotate(-90, 15, ${chartHeight / 2})`}>
          Power (kW)
        </text>
        
        {/* Legend */}
        <g transform={`translate(${chartWidth - 120}, 25)`}>
          <rect x="0" y="0" width="110" height="50" fill="rgba(0,0,0,0.7)" rx="5"/>
          <line x1="10" y1="15" x2="25" y2="15" stroke="#4CAF50" strokeWidth="2"/>
          <text x="30" y="19" fontSize="10" fill="#fff">Export</text>
          <line x1="10" y1="30" x2="25" y2="30" stroke="#f44336" strokeWidth="2"/>
          <text x="30" y="34" fontSize="10" fill="#fff">Import</text>
          <line x1="10" y1="42" x2="25" y2="42" stroke="#ff6b6b" strokeWidth="2" strokeDasharray="3,3"/>
          <text x="30" y="46" fontSize="10" fill="#fff">Limit</text>
        </g>
      </svg>
    </div>
  );
};

const Overview: React.FC = () => {
  const [energyData, setEnergyData] = useState<EnergyData | null>(null);
  const [settings, setSettings] = useState<EnergyOverviewSettings | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [gridHistory, setGridHistory] = useState<GridDataPoint[]>([]);
  const [selectedTimeFrame, setSelectedTimeFrame] = useState<number>(30 * 1000); // Default to 30 seconds

  useEffect(() => {
    const fetchEnergyData = async () => {
      try {
        const response = await gatewayService.getEnergyOverview();
        const processedData = processEnergyData(response);
        setEnergyData(processedData);
        console.log(processedData);
        setSettings(response.settings);
        
        // Add current grid power to history
        const now = Date.now();
        const newDataPoint: GridDataPoint = {
          timestamp: now,
          power: processedData.grid.net
        };
        
        setGridHistory(prev => {
          const updated = [...prev, newDataPoint];
          // Keep data for the longest timeframe (20 minutes) to allow switching
          const maxTimeFrame = 20 * 60 * 1000;
          const cutoffTime = now - maxTimeFrame;
          return updated.filter(point => point.timestamp >= cutoffTime);
        });
        
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
    const interval = setInterval(fetchEnergyData, 1000);
    
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
    <div css={css`
      width: 100%;
      max-width: 600px;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 0 10px;
    `}>
      {/* Energy Flow Visualization - Compact for side-by-side */}
      <div css={css`
        width: 100%;
        max-width: 500px;
        background: rgba(26, 26, 46, 0.8);
        border-radius: 12px;
        border: 1px solid #444;
        padding: 20px;
      `}>
        <h2 css={css`
          color: #fff;
          margin: 0 0 5px 0;
          font-size: 18px;
          text-align: center;
        `}>Energy System Overview</h2>
        <p css={css`
          color: #ccc;
          margin: 0 0 15px 0;
          font-size: 12px;
          text-align: center;
        `}>Real-time energy flow visualization</p>
        
        <div css={css`
          ${FlowWrapper};
          transform: scale(0.8);
          transform-origin: center;
          margin: -20px;
        `}>
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
                {energyData.battery.isCharging ? (
                  <UilArrowDown style={ArrowColorStyle('lightblue')} />
                ) : energyData.battery.isDischarging ? (
                  <UilArrowUp style={ArrowColorStyle('#e69373')} />
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
    </div>
  );
};

export default Overview;