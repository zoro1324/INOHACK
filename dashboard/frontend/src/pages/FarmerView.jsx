// src/pages/FarmerView.jsx
import React, { useState } from 'react';
import AlertBanner from '../components/AlertBanner';
import MapView from '../components/MapView';

const FarmerView = () => {
  const [currentAlert] = useState({
    animal: 'Elephant',
    location: 'North Field - Sector 3',
    time: '2:34 PM',
    cameraId: 'CAM-007'
  });

  const mockDetections = [
    { x: 30, y: 40 },
    { x: 60, y: 50 }
  ];

  return (
    <div className="min-h-screen bg-earth-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-earth-800 mb-2">Farmer Dashboard</h1>
          <p className="text-earth-600">Monitor your farm for wildlife activity</p>
        </div>

        <AlertBanner alert={currentAlert} />

        <div className="mb-6">
          <MapView detections={mockDetections} />
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-2xl font-bold text-earth-800 mb-4">Detection Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-earth-100 p-4 rounded-lg">
              <p className="text-sm text-earth-600 mb-1">Animal Type</p>
              <p className="text-2xl font-bold text-earth-800">{currentAlert.animal}</p>
            </div>
            <div className="bg-earth-100 p-4 rounded-lg">
              <p className="text-sm text-earth-600 mb-1">Time Detected</p>
              <p className="text-2xl font-bold text-earth-800">{currentAlert.time}</p>
            </div>
            <div className="bg-earth-100 p-4 rounded-lg">
              <p className="text-sm text-earth-600 mb-1">Location</p>
              <p className="text-2xl font-bold text-earth-800">{currentAlert.location}</p>
            </div>
            <div className="bg-earth-100 p-4 rounded-lg">
              <p className="text-sm text-earth-600 mb-1">Camera ID</p>
              <p className="text-2xl font-bold text-earth-800">{currentAlert.cameraId}</p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="bg-green-600 hover:bg-green-700 text-white text-xl font-bold py-6 px-8 rounded-lg shadow-lg transition">
            SAFE NOW
          </button>
          <button className="bg-yellow-600 hover:bg-yellow-700 text-white text-xl font-bold py-6 px-8 rounded-lg shadow-lg transition">
            CALL RANGER
          </button>
          <button className="bg-blue-600 hover:bg-blue-700 text-white text-xl font-bold py-6 px-8 rounded-lg shadow-lg transition">
            VIEW HISTORY
          </button>
        </div>
      </div>
    </div>
  );
};

export default FarmerView;
