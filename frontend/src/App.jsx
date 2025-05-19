import React from 'react';
import VideoFeed from './components/VideoFeed';
import AlertPanel from './components/AlertPanel';

const App = () => {
  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <h1 className="text-3xl font-bold text-center mb-6">Clinisight Caregiver Dashboard</h1>
      <div className="bg-blue-500 text-white p-4 rounded mb-4">Tailwind CSS v3 Test</div>
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-4">Live Video Feed</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <VideoFeed roomId="101" />
          <VideoFeed roomId="102" />
        </div>
      </div>
      <AlertPanel />
    </div>
  );
};

export default App;