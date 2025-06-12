import React from 'react';
import Overview from './components/EnergyOverview/Overview';
import DeviceManager from './components/DeviceManager/DeviceManager';
import GridPowerChart from './components/GridPowerChart/GridPowerChart';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Grid Power Chart at the top */}
        <div className="mb-[100px]">
          <GridPowerChart />
        </div>
        
        {/* Two columns below */}
        <div className="flex flex-col md:flex-row gap-6 items-start">
          <Overview />
          <DeviceManager />
        </div>
      </div>
    </div>
  );
};

export default App; 