// src/pages/PublicView.jsx
import React, { useState } from 'react';
import MapView from '../components/MapView';

const PublicView = () => {
  const [safetyZones] = useState([
    { x: 20, y: 30, size: 80, safe: true },
    { x: 60, y: 50, size: 60, safe: false },
    { x: 40, y: 70, size: 70, safe: true },
  ]);

  const [stats] = useState({
    totalDetections: 487,
    activeAreas: 6,
    safeZones: 12,
    lastUpdate: '5 mins ago'
  });

  return (
    <div className="min-h-screen bg-earth-50 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-gradient-to-r from-green-700 to-green-500 rounded-lg shadow-lg p-8 mb-6 text-white">
          <h1 className="text-4xl font-bold mb-3">Wildlife Awareness Portal</h1>
          <p className="text-lg text-green-100">Real-time information about wildlife movement in your area</p>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-6 mb-6 rounded-r-lg">
          <div className="flex items-start">
            <svg className="w-6 h-6 text-blue-500 mr-3 mt-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <h3 className="text-lg font-bold text-blue-900 mb-2">About This System</h3>
              <p className="text-blue-800">
                This public awareness portal provides general information about wildlife activity in your region. 
                The data shown is for educational purposes and helps communities understand wildlife patterns. 
                For real-time alerts and emergency information, please contact local authorities.
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="bg-earth-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
              <svg className="w-8 h-8 text-earth-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-earth-800">{stats.totalDetections}</p>
            <p className="text-sm text-earth-600">Total Detections</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="bg-yellow-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
              <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-earth-800">{stats.activeAreas}</p>
            <p className="text-sm text-earth-600">Active Areas</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="bg-green-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-earth-800">{stats.safeZones}</p>
            <p className="text-sm text-earth-600">Safe Zones</p>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6 text-center">
            <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-3">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <p className="text-2xl font-bold text-earth-800">{stats.lastUpdate}</p>
            <p className="text-sm text-earth-600">Last Update</p>
          </div>
        </div>

        <div className="mb-6">
          <MapView zones={safetyZones} />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-earth-800 mb-4">Common Wildlife</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-earth-50 rounded">
                <span className="font-medium text-earth-800">Elephants</span>
                <span className="text-sm text-earth-600">Most active at dusk</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-earth-50 rounded">
                <span className="font-medium text-earth-800">Wild Boars</span>
                <span className="text-sm text-earth-600">Common in forests</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-earth-50 rounded">
                <span className="font-medium text-earth-800">Deer</span>
                <span className="text-sm text-earth-600">Harmless grazers</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-earth-50 rounded">
                <span className="font-medium text-earth-800">Leopards</span>
                <span className="text-sm text-earth-600">Rare sightings</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-earth-800 mb-4">Safety Guidelines</h3>
            <ul className="space-y-3">
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-earth-700">Stay in designated safe zones during high activity hours</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-earth-700">Keep a safe distance if you encounter wildlife</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-earth-700">Report any unusual activity to local authorities</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 text-green-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-earth-700">Do not feed or provoke wild animals</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="bg-earth-700 text-white rounded-lg shadow-lg p-6 text-center">
          <h3 className="text-2xl font-bold mb-3">Need Help?</h3>
          <p className="mb-4">Contact local wildlife authorities for emergencies or concerns</p>
          <button className="bg-white text-earth-700 px-8 py-3 rounded-lg font-bold hover:bg-earth-100 transition">
            Emergency Contact
          </button>
        </div>
      </div>
    </div>
  );
};

export default PublicView;
