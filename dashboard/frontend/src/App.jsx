// src/App.jsx
import React from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import FarmerView from './pages/FarmerView';
import RangerDashboard from './pages/RangerDashboard';
import PublicView from './pages/PublicView';

const RoleSwitcher = () => {
  const { role, switchRole } = useAuth();

  return (
    <div className="fixed top-4 right-4 z-50 bg-white rounded-lg shadow-lg p-4">
      <p className="text-sm text-earth-600 mb-2 font-medium">Switch Role:</p>
      <div className="flex space-x-2">
        <button
          onClick={() => switchRole('farmer')}
          className={`px-4 py-2 rounded font-medium transition ${
            role === 'farmer'
              ? 'bg-earth-600 text-white'
              : 'bg-earth-100 text-earth-700 hover:bg-earth-200'
          }`}
        >
          Farmer
        </button>
        <button
          onClick={() => switchRole('ranger')}
          className={`px-4 py-2 rounded font-medium transition ${
            role === 'ranger'
              ? 'bg-earth-600 text-white'
              : 'bg-earth-100 text-earth-700 hover:bg-earth-200'
          }`}
        >
          Ranger
        </button>
        <button
          onClick={() => switchRole('public')}
          className={`px-4 py-2 rounded font-medium transition ${
            role === 'public'
              ? 'bg-earth-600 text-white'
              : 'bg-earth-100 text-earth-700 hover:bg-earth-200'
          }`}
        >
          Public
        </button>
      </div>
    </div>
  );
};

const AppContent = () => {
  const { role } = useAuth();

  return (
    <>
      <RoleSwitcher />
      {role === 'farmer' && <FarmerView />}
      {role === 'ranger' && <RangerDashboard />}
      {role === 'public' && <PublicView />}
    </>
  );
};

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
