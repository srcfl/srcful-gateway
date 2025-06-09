import React from 'react';
import Overview from './components/EnergyOverview/Overview';

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 p-4">
      <div className="flex items-center justify-center min-h-screen">
        <Overview />
      </div>
    </div>
  );
};

export default App; 