// src/context/AuthContext.jsx
import React, { createContext, useContext, useState } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [role, setRole] = useState('farmer');

  const switchRole = (newRole) => {
    setRole(newRole);
  };

  return (
    <AuthContext.Provider value={{ role, switchRole }}>
      {children}
    </AuthContext.Provider>
  );
};
