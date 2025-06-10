import React from 'react';
import Overview from './components/EnergyOverview/Overview';
import DeviceManager from './components/DeviceManager/DeviceManager';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          <div className="flex items-center justify-center">
            <Overview />
          </div>
          <div className="flex items-center justify-center">
            <DeviceManager />
          </div>
        </div>
      </div>
    </div>
  );
};

export default App; 