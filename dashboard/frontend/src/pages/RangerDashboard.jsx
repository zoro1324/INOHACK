// src/pages/RangerDashboard.jsx
import React, { useState } from 'react';
import MapView from '../components/MapView';

const RangerDashboard = () => {
  const [cameras] = useState([
    { id: 'CAM-001', status: 'online', battery: 85, location: 'North Gate' },
    { id: 'CAM-002', status: 'online', battery: 92, location: 'East Field' },
    { id: 'CAM-003', status: 'offline', battery: 12, location: 'South Border' },
    { id: 'CAM-004', status: 'online', battery: 67, location: 'West Forest' },
    { id: 'CAM-005', status: 'online', battery: 78, location: 'Central Farm' },
    { id: 'CAM-006', status: 'online', battery: 95, location: 'River Bank' },
  ]);

  const [recentDetections] = useState([
    { id: 1, animal: 'Elephant', location: 'North Gate', time: '10 mins ago', severity: 'high' },
    { id: 2, animal: 'Wild Boar', location: 'East Field', time: '25 mins ago', severity: 'medium' },
    { id: 3, animal: 'Deer', location: 'West Forest', time: '1 hour ago', severity: 'low' },
    { id: 4, animal: 'Leopard', location: 'South Border', time: '2 hours ago', severity: 'high' },
    { id: 5, animal: 'Monkey', location: 'Central Farm', time: '3 hours ago', severity: 'low' },
  ]);

  const mockDetections = [
    { x: 20, y: 30 },
    { x: 45, y: 55 },
    { x: 70, y: 40 }
  ];

  return (
    <div className="min-h-screen bg-earth-50 p-4 md:p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-earth-700 to-earth-500 rounded-lg shadow-lg p-6 mb-6 text-white">
          <h1 className="text-3xl font-bold mb-2">Ranger Control Center</h1>
          <p className="text-earth-100">Real-time monitoring and wildlife management</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-earth-600 text-sm">Active Cameras</p>
                <p className="text-3xl font-bold text-earth-800">5/6</p>
              </div>
              <div className="bg-green-100 rounded-full p-3">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-earth-600 text-sm">Today's Alerts</p>
                <p className="text-3xl font-bold text-earth-800">12</p>
              </div>
              <div className="bg-yellow-100 rounded-full p-3">
                <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-earth-600 text-sm">High Priority</p>
                <p className="text-3xl font-bold text-red-600">3</p>
              </div>
              <div className="bg-red-100 rounded-full p-3">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-earth-600 text-sm">Avg Response</p>
                <p className="text-3xl font-bold text-earth-800">8m</p>
              </div>
              <div className="bg-blue-100 rounded-full p-3">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <MapView detections={mockDetections} showControls={true} />
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-bold text-earth-800 mb-4">Camera Status</h3>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {cameras.map((camera) => (
                <div key={camera.id} className="border border-earth-200 rounded-lg p-3">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <p className="font-bold text-earth-800">{camera.id}</p>
                      <p className="text-sm text-earth-600">{camera.location}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      camera.status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {camera.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <div className="flex-1 bg-earth-200 rounded-full h-2 mr-2">
                      <div 
                        className={`h-2 rounded-full ${
                          camera.battery > 50 ? 'bg-green-500' : camera.battery > 20 ? 'bg-yellow-500' : 'bg-red-500'
                        }`}
                        style={{ width: `${camera.battery}%` }}
                      ></div>
                    </div>
                    <span className="text-xs text-earth-600">{camera.battery}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-bold text-earth-800">Recent Detections</h3>
            <button className="text-earth-600 hover:text-earth-800 text-sm font-medium">
              View All →
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-earth-200">
                  <th className="text-left py-3 px-4 text-earth-600 font-semibold">Animal</th>
                  <th className="text-left py-3 px-4 text-earth-600 font-semibold">Location</th>
                  <th className="text-left py-3 px-4 text-earth-600 font-semibold">Time</th>
                  <th className="text-left py-3 px-4 text-earth-600 font-semibold">Severity</th>
                  <th className="text-left py-3 px-4 text-earth-600 font-semibold">Action</th>
                </tr>
              </thead>
              <tbody>
                {recentDetections.map((detection) => (
                  <tr key={detection.id} className="border-b border-earth-100 hover:bg-earth-50">
                    <td className="py-3 px-4 font-medium text-earth-800">{detection.animal}</td>
                    <td className="py-3 px-4 text-earth-600">{detection.location}</td>
                    <td className="py-3 px-4 text-earth-600">{detection.time}</td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        detection.severity === 'high' ? 'bg-red-100 text-red-800' :
                        detection.severity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-green-100 text-green-800'
                      }`}>
                        {detection.severity.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <button className="text-earth-600 hover:text-earth-800 text-sm font-medium">
                        Details →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RangerDashboard;
