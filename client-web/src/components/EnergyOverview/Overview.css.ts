import { css } from '@emotion/react';

export const OverviewWrapperStyle = css`
  padding: 20px;
  background: #1a1a2e;
  border-radius: 12px;
  margin: 20px;
  
  h2 {
    margin-bottom: 8px;
    color: #fff;
    font-size: 24px;
  }
  
  p {
    color: #ccc;
    margin-bottom: 20px;
    font-size: 14px;
  }
`;

export const FlowWrapper = css`
  position: relative;
  width: 500px;
  height: 500px;
  margin: 0 auto;
  
  .curve, .line {
    position: absolute;
    pointer-events: none;
  }
  
  .animate-particle {
    .particle {
      stroke-dasharray: 5;
      animation: dash 2s linear infinite;
    }
  }
  
  @keyframes dash {
    to {
      stroke-dashoffset: -10;
    }
  }
`;

export const Circle = css`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: rgba(42, 42, 64, 0.8);
  border: 3px solid #444;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  position: absolute;
  z-index: 10;
  
  &.inactive {
    opacity: 0.3;
    background: rgba(42, 42, 64, 0.4);
    border-color: #333;
    
    svg {
      opacity: 0.3;
    }
  }
  
  svg {
    margin-bottom: 8px;
    color: #fff;
  }
  
  span {
    font-weight: bold;
    font-size: 16px;
    color: #fff;
    text-align: center;
    
    span {
      font-size: 12px;
      font-weight: normal;
      color: #ccc;
      text-transform: lowercase;
    }
    
    &.in, &.out {
      display: flex;
      align-items: center;
      gap: 4px;
      font-size: 11px;
      margin: 1px 0;
      color: #ccc;
    }
  }
`;

export const SolarCircle = css`
  top: 50px;
  left: 180px;
  border-color: #ffa500;
  background: rgba(42, 42, 64, 0.9);
  
  &:not(.inactive) {
    box-shadow: 0 4px 20px rgba(255, 165, 0, 0.4);
    border-color: #ffa500;
  }
  
  svg {
    color: #ffa500;
  }
`;

export const GridCircle = css`
  top: 180px;
  left: 50px;
  border-color: #666;
  background: rgba(42, 42, 64, 0.9);
  
  &:not(.inactive) {
    box-shadow: 0 4px 20px rgba(100, 100, 150, 0.4);
    border-color: #666;
  }
  
  svg {
    color: #888;
  }
`;

export const HomeCircle = css`
  top: 180px;
  right: 50px;
  border-color: #4a90e2;
  background: rgba(42, 42, 64, 0.9);
  box-shadow: 0 4px 20px rgba(74, 144, 226, 0.4);
  
  svg {
    color: #4a90e2;
  }
`;

export const BatteryCircle = css`
  bottom: 50px;
  left: 180px;
  border-color: #6f42c1;
  background: rgba(42, 42, 64, 0.6);
  
  &:not(.inactive) {
    box-shadow: 0 4px 20px rgba(111, 66, 193, 0.4);
  }
  
  svg {
    color: #6f42c1;
  }
`;

export const CurveStyle = css`
  width: 40px;
  height: 40px;
  
  path {
    fill: none;
    stroke: #444;
    stroke-width: 2;
    
    &.particle {
      stroke: #ffa500;
      stroke-width: 3;
    }
  }
  
  &.export-solar-to-grid {
    top: 195px;
    left: 190px;
    transform: rotate(-90deg);
  }
  
  &.export-solar-to-house {
    top: 195px;
    left: 270px;
    transform: rotate(0deg);
  }
  
  &.import-export-battery-to-grid {
    bottom: 190px;
    left: 190px;
    transform: rotate(-180deg);
    
    path.particle {
      stroke: #888;
      stroke-width: 3;
    }
  }
  
  &.export-battery-to-house {
    bottom: 190px;
    right: 190px;
    transform: rotate(90deg);
    
    path.particle {
      stroke: #6f42c1;
      stroke-width: 3;
    }
  }
`;

export const LineStyle = css`
  width: 120px;
  height: 20px;
  
  line {
    stroke: #444;
    stroke-width: 2;
    
    &.particle {
      stroke: #4a90e2;
      stroke-width: 3;
    }
  }
  
  &.export-solar-to-battery {
    top: 240px;
    left: 190px;
    transform: rotate(90deg);
    
    line.particle {
      stroke: #ffa500;
      stroke-width: 3;
    }
  }
  
  &.import-grid-to-house {
    top: 240px;
    left: 190px;
    transform: rotate(0deg);
    
    line.particle {
      stroke: #888;
      stroke-width: 3;
    }
  }
`; 