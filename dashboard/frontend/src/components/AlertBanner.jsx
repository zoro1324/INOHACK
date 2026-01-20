// src/components/AlertBanner.jsx
import React from 'react';

const AlertBanner = ({ alert }) => {
  if (!alert) return null;

  return (
    <div className="bg-red-600 text-white p-6 rounded-lg shadow-lg mb-6 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="bg-white rounded-full p-3">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <h2 className="text-2xl font-bold">{alert.animal} DETECTED!</h2>
            <p className="text-lg mt-1">{alert.location}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xl font-semibold">{alert.time}</p>
          <p className="text-sm">Camera {alert.cameraId}</p>
        </div>
      </div>
    </div>
  );
};

export default AlertBanner;
