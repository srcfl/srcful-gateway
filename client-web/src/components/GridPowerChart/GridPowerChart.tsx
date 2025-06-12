/** @jsxImportSource @emotion/react */
import React, { useState, useEffect } from 'react';
import { css } from '@emotion/react';
import { gatewayService, GatewayApiError } from '../../services/GatewayService';
import { EnergyOverviewResponse, EnergyOverviewSettings } from '../../types/api';

// Grid data point structure for the chart
interface GridDataPoint {
  timestamp: number;
  power: number; // Grid power in kW
}

// Energy data structure (needed for processing)
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

// Time frame options
const TIME_FRAMES = [
  { label: '30s', value: 30 * 1000 },
  { label: '1m', value: 60 * 1000 },
  { label: '5m', value: 5 * 60 * 1000 },
  { label: '10m', value: 10 * 60 * 1000 },
  { label: '15m', value: 15 * 60 * 1000 },
  { label: '20m', value: 20 * 60 * 1000 },
];

// Process DEE data into our energy structure (simplified version for grid data)
const processEnergyData = (deeData: EnergyOverviewResponse): EnergyData => {
  let gridImport = 0;   
  let gridExport = 0;   

  deeData.data.dee.forEach(item => {
    if (item.meter) {
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

  const netGridFlow = gridExport - gridImport;
  
  return {
    solar: { power: 0, isActive: true },
    grid: { net: netGridFlow / 1000, isActive: true },
    home: { load_power: 0 },
    battery: { net: 0, isActive: true }
  };
};

// Chart Component
const Chart: React.FC<{ 
  data: GridDataPoint[], 
  gridLimit: number,
  selectedTimeFrame: number,
  onTimeFrameChange: (timeFrame: number) => void
}> = ({ data, gridLimit, selectedTimeFrame, onTimeFrameChange }) => {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const [chartWidth, setChartWidth] = React.useState(1200);
  const chartHeight = 200;
  const padding = { top: 20, right: 30, bottom: 30, left: 50 };
  const plotWidth = chartWidth - padding.left - padding.right;
  const plotHeight = chartHeight - padding.top - padding.bottom;

  // Update chart width based on container size
  React.useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.offsetWidth - 20; // Account for padding
        setChartWidth(containerWidth > 0 ? containerWidth : 1200); // Use actual container width
      }
    };

    // Use ResizeObserver for better responsiveness
    const resizeObserver = new ResizeObserver(() => {
      updateWidth();
    });

    if (containerRef.current) {
      resizeObserver.observe(containerRef.current);
    }

    // Initial sizing with multiple attempts
    updateWidth();
    const timer1 = setTimeout(updateWidth, 50);
    const timer2 = setTimeout(updateWidth, 200);
    
    window.addEventListener('resize', updateWidth);
    return () => {
      window.removeEventListener('resize', updateWidth);
      resizeObserver.disconnect();
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, []);

  // Filter data for selected time frame
  const now = Date.now();
  const startTime = now - selectedTimeFrame;
  const filteredData = data.filter(point => point.timestamp >= startTime);

  // Scale functions (needed for useMemo)
  const maxAbsPower = React.useMemo(() => {
    if (!filteredData.length) return 1;
    return Math.max(
      Math.abs(Math.min(...filteredData.map(d => d.power))),
      Math.abs(Math.max(...filteredData.map(d => d.power))),
      gridLimit / 1000 // Include grid limit in scaling
    );
  }, [filteredData, gridLimit]);
  
  const yRange = maxAbsPower * 1.2; // Add 20% padding

  const scaleX = React.useCallback((timestamp: number) => {
    const relativeTime = timestamp - startTime;
    return padding.left + (relativeTime / selectedTimeFrame) * plotWidth;
  }, [startTime, selectedTimeFrame, plotWidth]);

  const scaleY = React.useCallback((power: number) => {
    return padding.top + plotHeight / 2 - (power / yRange) * (plotHeight / 2);
  }, [yRange, plotHeight]);

  // Create efficient colored path segments (moved to top level)
  const pathSegments = React.useMemo(() => {
    if (filteredData.length < 2) return { importSegments: '', exportSegments: '' };
    
    const importPaths: string[] = [];
    const exportPaths: string[] = [];
    
    for (let i = 0; i < filteredData.length - 1; i++) {
      const current = filteredData[i];
      const next = filteredData[i + 1];
      
      const x1 = scaleX(current.timestamp);
      const y1 = scaleY(-current.power);
      const x2 = scaleX(next.timestamp);
      const y2 = scaleY(-next.power);
      
      // Check if segment crosses zero line
      const currentDisplayPower = -current.power;
      const nextDisplayPower = -next.power;
      
      if ((currentDisplayPower >= 0 && nextDisplayPower >= 0) || 
          (currentDisplayPower > 0 && nextDisplayPower < 0 && currentDisplayPower > Math.abs(nextDisplayPower)) ||
          (currentDisplayPower < 0 && nextDisplayPower > 0 && nextDisplayPower > Math.abs(currentDisplayPower))) {
        // Segment is mostly in positive area (import = green)
        importPaths.push(`M ${x1} ${y1} L ${x2} ${y2}`);
      } else if ((currentDisplayPower <= 0 && nextDisplayPower <= 0) ||
                 (currentDisplayPower < 0 && nextDisplayPower > 0 && Math.abs(currentDisplayPower) > nextDisplayPower) ||
                 (currentDisplayPower > 0 && nextDisplayPower < 0 && Math.abs(nextDisplayPower) > currentDisplayPower)) {
        // Segment is mostly in negative area (export = red)  
        exportPaths.push(`M ${x1} ${y1} L ${x2} ${y2}`);
      } else {
        // Mixed segment - determine by midpoint
        const midDisplayPower = (currentDisplayPower + nextDisplayPower) / 2;
        if (midDisplayPower >= 0) {
          importPaths.push(`M ${x1} ${y1} L ${x2} ${y2}`);
        } else {
          exportPaths.push(`M ${x1} ${y1} L ${x2} ${y2}`);
        }
      }
    }
    
    return {
      importSegments: importPaths.join(' '),
      exportSegments: exportPaths.join(' ')
    };
  }, [filteredData, scaleX, scaleY]);

  if (!filteredData.length) {
    return (
      <div 
        ref={containerRef}
        css={css`
          background: rgba(42, 42, 64, 0.3);
          border-radius: 8px;
          border: 1px solid #666;
          padding: 10px;
          width: 100%;
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
          width: 100%;
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


  
  // Get latest point for power display
  const latestPoint = filteredData[filteredData.length - 1];
  const latestX = latestPoint ? scaleX(latestPoint.timestamp) : 0;
  const latestY = latestPoint ? scaleY(-latestPoint.power) : 0;
  const currentPower = latestPoint ? latestPoint.power : 0;

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
    <div 
      ref={containerRef}
      css={css`
        background: rgba(42, 42, 64, 0.3);
        border-radius: 8px;
        border: 1px solid #666;
        padding: 10px;
        width: 100%;
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
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
      `}>
        <h3 css={css`
          margin: 0;
          font-size: 14px;
          color: #fff;
          flex: 1;
          text-align: center;
        `}>
          Grid Power ({TIME_FRAMES.find(tf => tf.value === selectedTimeFrame)?.label})
        </h3>
        
        {/* Legend moved to top right */}
        <div css={css`
          display: flex;
          gap: 12px;
          font-size: 10px;
          color: #fff;
          background: rgba(0,0,0,0.7);
          padding: 8px 12px;
          border-radius: 5px;
        `}>
          <div css={css`display: flex; align-items: center; gap: 4px;`}>
            <div css={css`width: 12px; height: 2px; background: #4CAF50;`}></div>
            <span>Import</span>
          </div>
          <div css={css`display: flex; align-items: center; gap: 4px;`}>
            <div css={css`width: 12px; height: 2px; background: #f44336;`}></div>
            <span>Export</span>
          </div>
          <div css={css`display: flex; align-items: center; gap: 4px;`}>
            <div css={css`width: 12px; height: 2px; background: #ff6b6b; border-top: 1px dashed #ff6b6b; border-bottom: 1px dashed #ff6b6b;`}></div>
            <span>Limit</span>
          </div>
        </div>
      </div>
      
      <svg width="100%" height={chartHeight} viewBox={`0 0 ${chartWidth} ${chartHeight}`}>
        {/* Animated Background grid */}
        <defs>
          <pattern id="grid" width="40" height="30" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 30" fill="none" stroke="#333" strokeWidth="1" opacity="0.3"/>
            <animateTransform
              attributeName="patternTransform"
              attributeType="XML"
              type="translate"
              values="0,0;40,0;0,0"
              dur="4s"
              repeatCount="indefinite"
            />
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
        
        {/* Import segments (green - positive area) */}
        {pathSegments.importSegments && (
          <path 
            d={pathSegments.importSegments} 
            fill="none" 
            stroke="#4CAF50"
            strokeWidth="2"
            css={css`
              transition: d 1s ease-out;
            `}
          />
        )}
        
        {/* Export segments (red - negative area) */}
        {pathSegments.exportSegments && (
          <path 
            d={pathSegments.exportSegments} 
            fill="none" 
            stroke="#f44336"
            strokeWidth="2"
            css={css`
              transition: d 1s ease-out;
            `}
          />
        )}
        
        {/* Data points with smooth transitions */}
        {filteredData.map((point, index) => {
          const isLatest = index === filteredData.length - 1;
          return (
            <circle
              key={`point-${point.timestamp}`}
              cx={scaleX(point.timestamp)}
              cy={scaleY(-point.power)}
              r={isLatest ? "3" : "2"}
              fill={point.power > 0 ? "#f44336" : "#4CAF50"}
              css={css`
                transition: cx 1s ease-out, cy 1s ease-out, opacity 0.3s ease-in-out;
                ${isLatest ? `
                  animation: pulse 2s ease-in-out infinite;
                  @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.7; }
                  }
                ` : ''}
              `}
            />
          );
        })}
        
        {/* Current power value display at head */}
        {latestPoint && (() => {
          const textContent = `${currentPower.toFixed(1)} kW`;
          const textWidth = textContent.length * 8 + 10; // More accurate width calculation
          const boxHeight = 24;
          
          // Calculate position, ensuring it stays within chart bounds
          let boxX = latestX + 10;
          let textX = boxX + 8;
          
          // If too close to right edge, position to the left of the dot
          if (boxX + textWidth > chartWidth - padding.right) {
            boxX = latestX - textWidth - 10;
            textX = boxX + 8;
          }
          
          // Ensure it doesn't go off the left edge either
          if (boxX < padding.left) {
            boxX = padding.left + 5;
            textX = boxX + 8;
          }
          
          const boxY = latestY - 15;
          const textY = boxY + 16;
          
          return (
            <g>
              {/* Background for text readability */}
              <rect
                x={boxX}
                y={boxY}
                width={textWidth}
                height={boxHeight}
                fill="rgba(0,0,0,0.9)"
                stroke={currentPower > 0 ? "#f44336" : "#4CAF50"}
                strokeWidth="1.5"
                rx="6"
                css={css`
                  transition: x 1s ease-out, y 1s ease-out;
                `}
              />
              {/* Power value text */}
              <text
                x={textX}
                y={textY}
                fill="#ffffff"
                fontSize="12"
                fontWeight="bold"
                fontFamily="monospace"
                css={css`
                  transition: x 1s ease-out, y 1s ease-out;
                `}
              >
                {textContent}
              </text>
            </g>
          );
        })()}
        
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
        

      </svg>
    </div>
  );
};

// Main GridPowerChart Component
const GridPowerChart: React.FC = () => {
  const [settings, setSettings] = useState<EnergyOverviewSettings | null>(null);
  const [gridHistory, setGridHistory] = useState<GridDataPoint[]>([]);
  const [selectedTimeFrame, setSelectedTimeFrame] = useState<number>(30 * 1000);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await gatewayService.getEnergyOverview();
        const processedData = processEnergyData(response);
        setSettings(response.settings);
        
        // Add current grid power to history
        const now = Date.now();
        const newDataPoint: GridDataPoint = {
          timestamp: now,
          power: processedData.grid.net
        };
        
        setGridHistory(prev => {
          const updated = [...prev, newDataPoint];
          const maxTimeFrame = 20 * 60 * 1000;
          const cutoffTime = now - maxTimeFrame;
          return updated.filter(point => point.timestamp >= cutoffTime);
        });
        
        setLoading(false);
      } catch (err) {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !settings) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-600">
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-300">Loading grid power data...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full bg-gray-800 rounded-lg p-6 border border-gray-600">
      {/* Power Limits Display */}
      <div className="flex justify-center gap-5 mb-6 text-sm">
        <div className="bg-gray-700 px-4 py-2 rounded-lg border border-gray-500">
          <span className="text-gray-400 font-medium">Grid Limit: </span>
          <span className="text-white font-semibold">{(settings.grid_power_limit / 1000).toFixed(1)} kW</span>
        </div>
        <div className="bg-gray-700 px-4 py-2 rounded-lg border border-purple-500">
          <span className="text-gray-400 font-medium">Battery Limit: </span>
          <span className="text-white font-semibold">{(settings.battery_power_limit / 1000).toFixed(1)} kW</span>
        </div>
      </div>
      
      <Chart 
        data={gridHistory} 
        gridLimit={settings.grid_power_limit}
        selectedTimeFrame={selectedTimeFrame}
        onTimeFrameChange={setSelectedTimeFrame}
      />
    </div>
  );
};

export default GridPowerChart; 