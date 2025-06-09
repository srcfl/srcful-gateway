/** @jsxImportSource @emotion/react */
import React from 'react';
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

// Hardcoded values for demonstration
const HARDCODED_DATA = {
  solar: {
    power: 3500, // 3.5 kW
    isActive: true
  },
  grid: {
    import: 1.2, // 1.2 kW from grid
    export: 0.8, // 0.8 kW to grid
    isActive: true
  },
  home: {
    consumption: 2.9 // 2.9 kW total consumption
  },
  battery: {
    charging: 1.5, // 1.5 kW charging
    discharging: 0, // 0 kW discharging
    isActive: true
  }
};

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

const getSystemState = () => {
  const solarKw = wattToKW(HARDCODED_DATA.solar.power);
  const gridExport = HARDCODED_DATA.grid.export;
  const gridImport = HARDCODED_DATA.grid.import;
  
  // Calculate energy flows
  const isExportingSolarToGrid = solarKw > 0 && gridExport > 0;
  const isExportingSolarToHouse = solarKw > 0 && (solarKw - gridExport) > 0;
  const isImportingGridToHouse = gridImport > 0;
  
  return {
    isExportingSolarToGrid,
    isExportingSolarToHouse,
    isImportingGridToHouse,
    houseConsumption: HARDCODED_DATA.home.consumption
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
  const state = getSystemState();

  return (
    <div css={OverviewWrapperStyle}>
      <h2>Energy overview (beta)</h2>
      <p>Real-time energy flow visualization</p>
      <div css={FlowWrapper}>
        {/* Solar Panel */}
        <div 
          css={[Circle, SolarCircle]} 
          className={HARDCODED_DATA.solar.isActive ? '' : 'inactive'}
        >
          <PvIcon />
          <span>
            {HARDCODED_DATA.solar.isActive ? wattToKW(HARDCODED_DATA.solar.power) : '-'}
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
          className={HARDCODED_DATA.grid.isActive ? '' : 'inactive'}
        >
          <GridIcon />
          <span className="in">
            <UilArrowLeft style={ArrowColorStyle('lightblue')} /> 
            {HARDCODED_DATA.grid.isActive ? formatNumber(HARDCODED_DATA.grid.export) : '-'} 
            <span>kW</span>
          </span>
          <span className="out">
            <UilArrowRight style={ArrowColorStyle('#e69373')} /> 
            {HARDCODED_DATA.grid.isActive ? formatNumber(HARDCODED_DATA.grid.import) : '-'} 
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
          className={HARDCODED_DATA.battery.isActive ? '' : 'inactive'}
        >
          <BatteryIcon css={css`width: 70px!important;`} />
          <span className="in">
            <UilArrowDown style={ArrowColorStyle('lightblue')} />
            {HARDCODED_DATA.battery.isActive ? formatNumber(HARDCODED_DATA.battery.charging) : '-'} 
            <span>kW</span>
          </span>
          <span className="out">
            <UilArrowUp style={ArrowColorStyle('#e69373')} />
            {HARDCODED_DATA.battery.isActive ? formatNumber(HARDCODED_DATA.battery.discharging) : '-'} 
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