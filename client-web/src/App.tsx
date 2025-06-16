import React, { useState, useEffect } from 'react';
import './App.css';

interface NetworkInfo {
  ip: string;
  port: number;
  eth0_mac: string;
  wlan0_mac: string;
  interfaces?: Record<string, string>;
}

const App: React.FC = () => {
  const [networkInfo, setNetworkInfo] = useState<NetworkInfo | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Test API call to your backend
    fetch('/api/network/address')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then((data: NetworkInfo) => {
        setNetworkInfo(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>Srcful Energy Gateway</h1>
        <h2>Web Client</h2>
        
        {loading && <p>Loading network information...</p>}
        
        {error && (
          <div style={{color: 'red'}}>
            <p>Error: {error}</p>
          </div>
        )}
        
        {networkInfo && (
          <div style={{textAlign: 'left', margin: '20px'}}>
            <h3>Network Information:</h3>
            <p><strong>IP:</strong> {networkInfo.ip}</p>
            <p><strong>Port:</strong> {networkInfo.port}</p>
            <p><strong>ETH0 MAC:</strong> {networkInfo.eth0_mac}</p>
            <p><strong>WLAN0 MAC:</strong> {networkInfo.wlan0_mac}</p>
            
            {networkInfo.interfaces && (
              <div>
                <h4>Network Interfaces:</h4>
                <ul>
                  {Object.entries(networkInfo.interfaces).map(([iface, ip]) => (
                    <li key={iface}><strong>{iface}:</strong> {ip}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        
        <p style={{fontSize: '14px', marginTop: '40px'}}>
          This React app is served through Traefik reverse proxy.<br/>
          API calls to <code>/api/*</code> are routed to your backend service.
        </p>
      </header>
    </div>
  );
};

export default App; 