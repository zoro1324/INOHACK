// src/components/MapView.jsx
import React from 'react';

const MapView = ({ zones, detections, showControls = false }) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-earth-800">Live Map View</h3>
        {showControls && (
          <div className="flex space-x-2">
            <button className="px-3 py-1 bg-earth-500 text-white rounded hover:bg-earth-600 text-sm">
              Zoom In
            </button>
            <button className="px-3 py-1 bg-earth-500 text-white rounded hover:bg-earth-600 text-sm">
              Zoom Out
            </button>
          </div>
        )}
      </div>
      
      <div className="relative bg-earth-100 rounded-lg h-96 overflow-hidden border-2 border-earth-300">
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <svg className="w-16 h-16 mx-auto text-earth-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
            </svg>
            <p className="text-earth-600 font-medium">Map Visualization</p>
          </div>
        </div>

        {zones && zones.map((zone, index) => (
          <div
            key={index}
            className={`absolute ${zone.safe ? 'bg-green-200' : 'bg-red-200'} opacity-30 rounded-full`}
            style={{
              left: `${zone.x}%`,
              top: `${zone.y}%`,
              width: `${zone.size}px`,
              height: `${zone.size}px`,
            }}
          />
        ))}

        {detections && detections.map((detection, index) => (
          <div
            key={index}
            className="absolute animate-ping"
            style={{ left: `${detection.x}%`, top: `${detection.y}%` }}
          >
            <div className="w-4 h-4 bg-red-600 rounded-full"></div>
          </div>
        ))}
      </div>

      {zones && (
        <div className="mt-4 flex space-x-4">
          <div className="flex items-center">
            <div className="w-4 h-4 bg-green-500 rounded mr-2"></div>
            <span className="text-sm text-earth-700">Safe Zone</span>
          </div>
          <div className="flex items-center">
            <div className="w-4 h-4 bg-red-500 rounded mr-2"></div>
            <span className="text-sm text-earth-700">Caution Zone</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default MapView;
